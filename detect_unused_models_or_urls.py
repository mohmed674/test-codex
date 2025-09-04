"""Scan project for unused Django models and named URLs.

This script builds a context from ``project_meta.json`` and then scans the
project source code and templates to determine which models or URL names are not
referenced anywhere.  The resulting information is written to
``unused_items_report.json``.

The original version of this file relied heavily on ``typing.cast`` which caused
static type checkers (and editors such as VS Code) to underline a number of
expressions in red.  The new implementation avoids the casts and retrieves
configuration values via ``dict.get`` which provides clearer types and keeps the
editor happy.
"""

from __future__ import annotations

import json
import os
import re
import sys
from typing import Dict, Iterable, List, Set, TypedDict

import django
from django.urls import get_resolver

from load_project_context import load_context


# ---------------------------------------------------------------------------
# Typing for project context (values are pulled from ``project_meta.json``)
# ---------------------------------------------------------------------------
class ProjectContext(TypedDict, total=False):
    project_root: str
    settings_module: str
    apps: Dict[str, List[str]]
    last_script: str


# ---------------------------------------------------------------------------
# Bootstrap Django context
# ---------------------------------------------------------------------------
context: ProjectContext = load_context()
BASE_DIR: str = context.get("project_root", "")
settings_module: str = context.get("settings_module", "")

if not BASE_DIR or not settings_module:
    raise RuntimeError("Missing project_root or settings_module in project context")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
django.setup()


# ---------------------------------------------------------------------------
# Containers
# ---------------------------------------------------------------------------
unused_models: Dict[str, List[str]] = {}
unused_url_names: List[str] = []


# ---------------------------------------------------------------------------
# Step 1: gather all project models
# ---------------------------------------------------------------------------
all_models: Dict[str, Dict[str, object]] = {}
for app, models in context.get("apps", {}).items():
    for model in models:
        all_models[model] = {"app": app, "used_in": []}


# ---------------------------------------------------------------------------
# Step 2: scan project files for model usage
# ---------------------------------------------------------------------------
def scan_usage(root_path: str, keywords: Iterable[str]) -> Dict[str, bool]:
    """Return a map indicating whether each keyword is found in the project."""

    usage: Dict[str, bool] = {key: False for key in keywords}
    for root, _, files in os.walk(root_path):
        for filename in files:
            if not filename.endswith((".py", ".html")):
                continue
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except (OSError, UnicodeDecodeError):
                # Skip unreadable files
                continue
            for key in keywords:
                if not usage[key] and key in content:
                    usage[key] = True
    return usage


model_usage = scan_usage(BASE_DIR, list(all_models.keys()))
for model, used in model_usage.items():
    if not used:
        app_name = all_models[model]["app"]
        app_models = context.get("apps", {}).get(app_name, [])
        unused_models[model] = app_models  # reference list of models for that app


# ---------------------------------------------------------------------------
# Step 3: extract named URLs from templates
# ---------------------------------------------------------------------------
def extract_url_names_from_templates(path: str) -> Set[str]:
    found: Set[str] = set()
    pattern = re.compile(r"{%\s*url\s+['\"]([\w:-]+)['\"]")
    for root, _, files in os.walk(path):
        for filename in files:
            if not filename.endswith(".html"):
                continue
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as fh:
                    content = fh.read()
            except (OSError, UnicodeDecodeError):
                # Skip files we cannot read
                continue
            found.update(pattern.findall(content))
    return found


templates_dir = os.path.join(BASE_DIR, "templates")
used_url_names = extract_url_names_from_templates(templates_dir)


# ---------------------------------------------------------------------------
# Step 4: compare with all defined named URLs
# ---------------------------------------------------------------------------
all_urls = get_resolver().reverse_dict.keys()
named_urls = {name for name in all_urls if isinstance(name, str)}
unused_url_names = list(named_urls - used_url_names)


# ---------------------------------------------------------------------------
# Step 5: save the report
# ---------------------------------------------------------------------------
report = {
    "unused_models": unused_models,
    "unused_url_names": unused_url_names,
}

with open(os.path.join(BASE_DIR, "unused_items_report.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("✅ تم إنشاء تقرير بالعناصر غير المستخدمة.")
print("📄 الملف: unused_items_report.json")


# ---------------------------------------------------------------------------
# Update project context for bookkeeping
# ---------------------------------------------------------------------------
context["last_script"] = "detect_unused_models_or_urls.py"
with open(os.path.join(BASE_DIR, "project_meta.json"), "w", encoding="utf-8") as f:
    json.dump(context, f, indent=2, ensure_ascii=False)

