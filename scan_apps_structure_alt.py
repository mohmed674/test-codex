# -*- coding: utf-8 -*-
"""
Scan Django-style apps tree and report presence of core files, templates, and an index view.

Why:
- Provide a quick completeness check across apps without crashing on unreadable files.
- Replace bare `except:` with explicit, safe error handling and logging.

Design:
- Deterministic output, preserves previous behavior (errors are ignored but now logged at DEBUG).
- Typed functions, small helpers, and line length ≤ 120.
"""

from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

LOG = logging.getLogger("scan_apps_structure_alt")

ROOT: Path = Path(__file__).resolve().parent
APPS_DIR: Path = ROOT / "apps"
FILES: Tuple[str, ...] = ("models.py", "views.py", "urls.py", "forms.py", "admin.py")

# Pre-compiled patterns for speed and clarity
PAT_FUNC_INDEX: re.Pattern[str] = re.compile(r"def\s+index\s*\(", re.IGNORECASE)
PAT_CBV_INDEX: re.Pattern[str] = re.compile(
    r"class\s+Index[A-Za-z0-9_]*\(", re.IGNORECASE
)
PAT_URLS_INDEX_TOKEN: re.Pattern[str] = re.compile(r"\bindex\b", re.IGNORECASE)


def configure_logging(verbosity: int = 0) -> None:
    """Configure basic logging. Use DEBUG for verbosity > 0."""
    level = logging.INFO if verbosity <= 0 else logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


def _safe_read_text(path: Path) -> Optional[str]:
    """
    Read text from a file safely, returning None on failure.

    We explicitly catch OSError/UnicodeDecodeError to avoid masking unexpected exceptions.
    """
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError) as exc:
        LOG.debug(
            "Failed to read %s: %s",
            path,
            exc,
            extra={"event": "read_failed", "path": str(path)},
        )
        return None


def has_index_view(app_path: Path) -> bool:
    """
    Detect presence of an 'index' view either as a function or CBV in views.py,
    or any reference to 'index' in urls.py. Failures to read files are ignored (return False).
    """
    views = app_path / "views.py"
    urls = app_path / "urls.py"

    if views.exists():
        content = _safe_read_text(views)
        if content and (
            PAT_FUNC_INDEX.search(content) or PAT_CBV_INDEX.search(content)
        ):
            return True

    if urls.exists():
        content = _safe_read_text(urls)
        if content and PAT_URLS_INDEX_TOKEN.search(content):
            return True

    return False


def has_templates_for(app_name: str, app_path: Path) -> bool:
    """
    Consider templates present if:
    - apps/<app>/templates/<app>/ exists, OR
    - apps/<app>/templates/ contains any .html/.htm files (recursively via os.walk).
    """
    a = app_path / "templates" / app_name
    b = app_path / "templates"
    if a.is_dir():
        return True
    if b.is_dir():
        for _, _, fs in os.walk(b):
            if any(f.lower().endswith((".html", ".htm")) for f in fs):
                return True
    return False


def is_app_dir(d: Path) -> bool:
    """An app dir is a real directory not starting with '__' (keeps previous behavior)."""
    return d.is_dir() and not d.name.startswith("__")


def line(label: str, ok: bool) -> str:
    """Format a status line with a checkmark/cross."""
    return f"   - {label:<12} {'✅' if ok else '❌'}"


def _iter_apps(base: Path) -> List[Path]:
    """Return sorted list of candidate app directories."""
    apps = [p for p in base.iterdir() if is_app_dir(p)]
    apps.sort(key=lambda p: p.name.lower())
    return apps


def main(argv: Optional[Sequence[str]] = None) -> int:
    configure_logging()

    if not APPS_DIR.is_dir():
        print(f"❌ لا يوجد مجلد apps في: {ROOT}")
        return 0

    apps = _iter_apps(APPS_DIR)
    print(f"\n🔍 فحص التطبيقات داخل: {APPS_DIR.name}\n")
    total = 0
    complete = 0

    for app_path in apps:
        total += 1
        app = app_path.name
        print(f"📦 [{app}]")
        status: Dict[str, bool] = {fn: (app_path / fn).exists() for fn in FILES}
        for fn, ok in status.items():
            print(line(fn, ok))

        tmpl_ok = has_templates_for(app, app_path)
        print(f"   - templates/{app}/ {'✅' if tmpl_ok else '❌'}")

        idx_ok = has_index_view(app_path)
        print(f"     ↪️ index {'✅' if idx_ok else '❌'}\n")

        if all(status.values()) and tmpl_ok:
            complete += 1

    print("============================================================")
    print("📊 ملخص")
    print("============================================================")
    print(f"إجمالي التطبيقات: {total}")
    print(f"تطبيقات مكتملة (ملفات أساسية + قوالب): {complete}/{total}")
    print("============================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
