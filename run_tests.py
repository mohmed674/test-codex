#!/usr/bin/env python3
# run_tests.py — مُشغِّل موحّد لاختبارات Django عبر Pytest

"""
تشغيل:
    python run_tests.py
    python run_tests.py -q -k "mytest"
    python run_tests.py tests/test_smoke.py::test_ok
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

# اجعل الجذر قابلًا للاستيراد
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# إعدادات Django الافتراضية للاختبار (يمكن تجاوزها بمتغيّر بيئي خارجي)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.pytest_settings")

# تلوين المخرجات إن لم تُحدّد خارجيًا
os.environ.setdefault("PYTEST_ADDOPTS", "")


def _precheck() -> int:
    """فحوصات خفيفة قبل تشغيل pytest."""
    # وجود إعدادات pytest المخصّصة
    if not (BASE_DIR / "config" / "pytest_settings.py").exists():
        print(
            "ERROR: الملف config/pytest_settings.py غير موجود. "
            "أنشئه أو حدّد DJANGO_SETTINGS_MODULE قبل التشغيل.",
            file=sys.stderr,
        )
        return 2

    # قدرة استيراد Django وpytest
    try:
        import django  # noqa: F401
    except Exception as e:  # pragma: no cover
        print(f"ERROR: تعذّر استيراد Django: {e}", file=sys.stderr)
        return 1

    try:
        import pytest  # noqa: F401
    except Exception as e:  # pragma: no cover
        print(f"ERROR: تعذّر استيراد pytest: {e}", file=sys.stderr)
        return 1

    return 0


def main(argv: list[str]) -> int:
    code = _precheck()
    if code != 0:
        return code

    import pytest

    # مرّر كل الوسائط إلى pytest (تعتمد التفصيلات الإضافية على pytest.ini)
    return pytest.main(argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
