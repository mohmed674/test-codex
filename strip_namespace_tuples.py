#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strip tuple-based include namespaces and standalone namespace=… from config/urls.py safely.

Why:
- Normalize `include((module, app_name), namespace='...')` -> `include('module')`
- Remove lone `namespace='...'` when include already takes a string module.
- Keep behavior, improve safety (no bare except), and provide typed, testable helpers.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence, Tuple

# ---------- Paths ----------
BASE: Path = Path(__file__).resolve().parent
CFG: Path = BASE / "config" / "urls.py"
STATE: Path = BASE / "project_state.json"

# ---------- Logging ----------
LOG = logging.getLogger("strip_namespace_tuples")


def configure_logging(verbosity: int = 0) -> None:
    level = logging.INFO if verbosity <= 0 else logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


# ---------- Regexes ----------
# 1) include(('apps.sales.urls','sales'), namespace='sales')  -> include('apps.sales.urls')
TUPLE_NS_RE: re.Pattern[str] = re.compile(
    r"include\(\(\s*['\"](?P<mod>[^'\"]+)['\"]\s*,\s*['\"][^'\"]+['\"]\s*\)"
    r"\s*,\s*namespace\s*=\s*['\"][^'\"]+['\"]\s*\)"
)

# 2) include('apps.sales.urls', namespace='sales') -> include('apps.sales.urls')
LONE_NS_RE: re.Pattern[str] = re.compile(
    r"include\(\s*(['\"][^'\"]+['\"])\s*,\s*namespace\s*=\s*['\"][^'\"]+['\"]\s*\)"
)

# 3) Cleanup: trailing comma before close paren: foo( ... , ) -> foo(...)
TRAIL_COMMA_RE: re.Pattern[str] = re.compile(r",\s*\)")


# ---------- IO Helpers ----------
def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        LOG.error(
            "urls.py not found: %s",
            path,
            extra={"event": "file_missing", "path": str(path)},
        )
        raise SystemExit(1) from exc
    except OSError as exc:
        LOG.error(
            "I/O error reading %s: %s",
            path,
            exc,
            extra={"event": "file_read_error", "path": str(path)},
        )
        raise SystemExit(1) from exc


def _write_text(path: Path, content: str) -> None:
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        LOG.error(
            "I/O error writing %s: %s",
            path,
            exc,
            extra={"event": "file_write_error", "path": str(path)},
        )
        raise SystemExit(1) from exc


# ---------- Core Transform ----------
def transform_source(src: str) -> Tuple[str, int, int, int]:
    """
    Apply the three normalization steps; return new source and counts of changes.
    """

    # Step 1: tuple + namespace
    def _tuple_sub(m: re.Match[str]) -> str:
        return f"include('{m.group('mod')}')"

    new_src, n1 = TUPLE_NS_RE.subn(_tuple_sub, src)

    # Step 2: lone namespace
    new_src, n2 = LONE_NS_RE.subn(r"include(\1)", new_src)

    # Step 3: trailing commas before ')'
    new_src, n3 = TRAIL_COMMA_RE.subn(")", new_src)

    return new_src, n1, n2, n3


# ---------- State ----------
def update_project_state(path: Path, updates: dict) -> None:
    """
    Merge updates into project_state.json. If unreadable or missing, recreate.
    """
    data: dict
    if path.exists():
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw) if raw.strip() else {}
        except (OSError, json.JSONDecodeError) as exc:
            LOG.warning(
                "Failed to read state: %s",
                exc,
                extra={"event": "state_read_failed", "path": str(path)},
            )
            data = {}
    else:
        data = {}

    data.update(updates)
    try:
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except OSError as exc:
        LOG.error(
            "Failed to write state: %s",
            exc,
            extra={"event": "state_write_failed", "path": str(path)},
        )


# ---------- CLI ----------
def main(argv: Optional[Sequence[str]] = None) -> int:
    configure_logging()

    src = _read_text(CFG)
    new_src, n1, n2, n3 = transform_source(src)

    if new_src != src:
        _write_text(CFG, new_src)

    now_iso = datetime.now(timezone.utc).isoformat()
    update_project_state(
        STATE,
        {
            "last_script": "strip_namespace_tuples.py",
            "status": "namespaces_stripped",
            "last_updated": now_iso,
            "changes": {
                "tuple_namespace": n1,
                "lone_namespace": n2,
                "trailing_commas": n3,
            },
        },
    )

    # Preserve user-facing print while also logging
    LOG.info(
        "Stripped namespace tuples from config/urls.py "
        "(tuple_ns=%d, lone_ns=%d, trailing_commas=%d)",
        n1,
        n2,
        n3,
        extra={"event": "strip_done"},
    )
    print("✅ Stripped namespace tuples from config/urls.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
