#!/usr/bin/env python3
"""
Deduplicate Django URL include targets in config/urls.py safely.

Why:
- Avoid duplicate include entries that can cause namespace/URL resolution conflicts.
- Normalize tuple-based include(...) to a canonical include('<module>') form.

Design:
- Non-destructive: preserves original ordering and non-include lines.
- Deterministic: identical input yields identical output.
- Safer I/O and error handling with explicit logging and typed functions.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set, Tuple

# ---------- Configuration ----------

BASE: Path = Path(__file__).resolve().parent
CFG: Path = BASE / "config" / "urls.py"
STATE: Path = BASE / "project_state.json"

URLPATTERNS_BLOCK_RE: re.Pattern[str] = re.compile(
    r"(urlpatterns\s*=\s*\[)(.*?)(\])", re.S
)
INCLUDE_TARGET_RE: re.Pattern[str] = re.compile(r"include\(\s*['\"]([^'\"]+)['\"]\s*\)")
# Match e.g.: include(('apps.sales.urls', 'sales'), namespace='sales')
TUPLE_INCLUDE_RE: re.Pattern[str] = re.compile(
    r"include\(\(\s*['\"][^'\"]+['\"].*?\)\s*,\s*namespace\s*=\s*['\"][^'\"]+['\"]\s*\)"
)

LOG = logging.getLogger("dedupe_url_includes")


@dataclass(frozen=True)
class DedupeResult:
    fixed_source: str
    removed_lines: Tuple[str, ...]
    targets_seen: Tuple[str, ...]


# ---------- Utilities ----------


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        LOG.error(
            "File not found: %s",
            path,
            extra={"event": "file_missing", "path": str(path)},
        )
        raise SystemExit(1) from exc
    except OSError as exc:
        LOG.error(
            "I/O error reading file: %s (%s)",
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
            "I/O error writing file: %s (%s)",
            path,
            exc,
            extra={"event": "file_write_error", "path": str(path)},
        )
        raise SystemExit(1) from exc


def _find_urlpatterns_block(src: str) -> Tuple[str, str, str, re.Match[str]]:
    m = URLPATTERNS_BLOCK_RE.search(src)
    if not m:
        LOG.error(
            "urlpatterns block not found in config/urls.py",
            extra={"event": "urlpatterns_missing"},
        )
        raise SystemExit(1)
    head, body, tail = m.group(1), m.group(2), m.group(3)
    return head, body, tail, m


def _normalize_tuple_include(line: str, target: str) -> str:
    """
    Convert tuple-based include with namespace to canonical include('<module>').
    Keeps other parts of the line intact.
    """
    return TUPLE_INCLUDE_RE.sub(f"include('{target}')", line)


def _dedupe_lines(lines: Sequence[str]) -> Tuple[List[str], List[str], Set[str]]:
    seen: Set[str] = set()
    new_lines: List[str] = []
    removed: List[str] = []

    for ln in lines:
        mo = INCLUDE_TARGET_RE.search(ln)
        if not mo:
            new_lines.append(ln)
            continue

        target = mo.group(1).strip()

        # If duplicate include target encountered, drop it.
        if target in seen:
            removed.append(ln.strip())
            continue
        seen.add(target)

        # Normalize tuple include with namespace -> include('module')
        normalized = _normalize_tuple_include(ln, target)
        new_lines.append(normalized)

    return new_lines, removed, seen


def dedupe_source(src: str) -> DedupeResult:
    """
    Perform deduplication on the given source text containing urlpatterns.
    Returns a DedupeResult with the fixed source and metadata.
    """
    head, body, tail, m = _find_urlpatterns_block(src)

    # Work line-by-line in the urlpatterns body to preserve formatting.
    body_lines = body.splitlines()
    new_lines, removed, seen = _dedupe_lines(body_lines)

    # Rebuild body, drop empty-only lines while preserving structure.
    new_body = "\n".join([ln for ln in new_lines if ln.strip()]) + "\n"
    fixed_source = src[: m.start(2)] + new_body + src[m.end(2) :]

    return DedupeResult(
        fixed_source=fixed_source,
        removed_lines=tuple(removed),
        targets_seen=tuple(sorted(seen)),
    )


def update_project_state(path: Path, updates: dict) -> None:
    """
    Merge updates into project_state.json. If the file is missing/corrupt,
    start from an empty dict. Writes atomically best-effort.
    """
    data: dict
    if path.exists():
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw) if raw.strip() else {}
        except (OSError, json.JSONDecodeError) as exc:
            LOG.warning(
                "State read failed, will recreate: %s",
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
        # Non-fatal for the main operation.
    return


def configure_logging(verbosity: int = 0) -> None:
    level = logging.INFO if verbosity <= 0 else logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(levelname)s %(message)s",
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    CLI entrypoint. Keeps same behavior (exit codes, side effects) but safer.
    """
    configure_logging()

    src = _read_text(CFG)
    result = dedupe_source(src)
    _write_text(CFG, result.fixed_source)

    now_iso = datetime.now(timezone.utc).isoformat()
    update_project_state(
        STATE,
        {
            "last_script": "dedupe_url_includes.py",
            "status": "urls_deduped",
            "last_updated": now_iso,
            "targets": list(result.targets_seen),
        },
    )

    if result.removed_lines:
        LOG.info(
            "Deduplicated include targets. Removed duplicates: %d",
            len(result.removed_lines),
            extra={"event": "dedupe_done", "removed_count": len(result.removed_lines)},
        )
        for r in result.removed_lines:
            LOG.info(" - %s", r)
    else:
        LOG.info("No duplicate include targets found.", extra={"event": "dedupe_done"})

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit as e:
        # Allow normal SystemExit propagation as is.
        raise
