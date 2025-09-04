# auto_generate_core_module.py
from __future__ import annotations

"""
Generate basic CRUD scaffolding for apps/core based on project_meta.json.

Creates:
- apps/core/forms.py
- apps/core/filters.py
- apps/core/serializers.py
- apps/core/views/<model>_views.py  (ListView/DetailView)
- apps/core/urls.py  (explicit imports per view module)

Notes:
- Uses explicit imports (no wildcard) to satisfy linters and Bandit.
- Idempotent: files are fully overwritten each run.
- Fails fast with clear errors; logs concise progress to stdout.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List

import django

BASE_DIR: Path = Path(__file__).resolve().parent
APPS_DIR: Path = BASE_DIR / "apps" / "core"
VIEWS_DIR: Path = APPS_DIR / "views"
META_PATH: Path = BASE_DIR / "project_meta.json"
STATE_PATH: Path = BASE_DIR / "project_state.json"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
django.setup()


def _read_meta(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"project_meta.json not found at: {path}")
    with path.open("r", encoding="utf-8") as f:
        meta = json.load(f)
    models = meta.get("apps", {}).get("core", [])
    if not isinstance(models, list):
        raise ValueError(
            "Invalid meta format: 'apps.core' must be a list of model names."
        )
    return [m for m in models if isinstance(m, str) and m.strip()]


def _write_forms(models: Iterable[str]) -> None:
    forms_path = APPS_DIR / "forms.py"
    lines: List[str] = [
        "from __future__ import annotations",
        "",
        "from django import forms",
        "from . import models",
        "",
    ]
    for model in models:
        lines += [
            f"class {model}Form(forms.ModelForm):",
            "    class Meta:",
            f"        model = models.{model}",
            "        fields = '__all__'",
            "",
        ]
    forms_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_filters(models: Iterable[str]) -> None:
    filters_path = APPS_DIR / "filters.py"
    lines: List[str] = [
        "from __future__ import annotations",
        "",
        "import django_filters",
        "from . import models",
        "",
    ]
    for model in models:
        lines += [
            f"class {model}Filter(django_filters.FilterSet):",
            "    class Meta:",
            f"        model = models.{model}",
            "        fields = '__all__'",
            "",
        ]
    filters_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_serializers(models: Iterable[str]) -> None:
    serializers_path = APPS_DIR / "serializers.py"
    lines: List[str] = [
        "from __future__ import annotations",
        "",
        "from rest_framework import serializers",
        "from . import models",
        "",
    ]
    for model in models:
        lines += [
            f"class {model}Serializer(serializers.ModelSerializer):",
            "    class Meta:",
            f"        model = models.{model}",
            "        fields = '__all__'",
            "",
        ]
    serializers_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_views(models: Iterable[str]) -> None:
    VIEWS_DIR.mkdir(parents=True, exist_ok=True)
    init_file = VIEWS_DIR / "__init__.py"
    if not init_file.exists():
        init_file.write_text("", encoding="utf-8")

    for model in models:
        view_path = VIEWS_DIR / f"{model.lower()}_views.py"
        lines: List[str] = [
            "from __future__ import annotations",
            "",
            "from django.views.generic import DetailView, ListView",
            f"from ..models import {model}",
            "",
            f"class {model}ListView(ListView):",
            f"    model = {model}",
            f"    template_name = 'core/{model.lower()}_list.html'",
            f"    context_object_name = '{model.lower()}_list'",
            "",
            f"class {model}DetailView(DetailView):",
            f"    model = {model}",
            f"    template_name = 'core/{model.lower()}_detail.html'",
            f"    context_object_name = '{model.lower()}'",
            "",
        ]
        view_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_urls(models: List[str]) -> None:
    urls_path = APPS_DIR / "urls.py"
    lines: List[str] = [
        "from __future__ import annotations",
        "",
        "from django.urls import path",
        "",
    ]
    # Explicit imports per view module to avoid wildcard imports.
    for model in models:
        mod = model.lower()
        lines.append(
            f"from .views.{mod}_views import {model}DetailView, {model}ListView"
        )
    lines += [
        "",
        "app_name = 'core'",
        "",
        "urlpatterns = [",
    ]
    for model in models:
        lname = model.lower()
        lines.append(
            f"    path('{lname}/', {model}ListView.as_view(), name='{lname}_list'),"
        )
        lines.append(
            f"    path('{lname}/<int:pk>/', {model}DetailView.as_view(), name='{lname}_detail'),"
        )
    lines.append("]")
    urls_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _update_state() -> None:
    state = {
        "last_script": "auto_generate_core_module.py",
        "next_script": None,
        "status": "core_module_generated",
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main() -> int:
    APPS_DIR.mkdir(parents=True, exist_ok=True)
    models = _read_meta(META_PATH)
    print(f"✅ جاري توليد الملفات داخل apps/core/ لـ {len(models)} موديل...\n")

    _write_forms(models)
    _write_filters(models)
    _write_serializers(models)
    _write_views(models)
    _write_urls(models)

    _update_state()
    print(
        "✅ تم توليد forms.py, filters.py, serializers.py, views/, urls.py بنجاح داخل apps/core/"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
