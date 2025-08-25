from pathlib import Path

BASE = Path(__file__).resolve().parent
pkg_dir = BASE / "apps" / "suppliers" / "urls"
pkg_dir.mkdir(parents=True, exist_ok=True)
init_file = pkg_dir / "__init__.py"

if not init_file.exists():
    init_file.write_text("# package init for suppliers.urls\n", encoding="utf-8")
    print("✅ created: apps/suppliers/urls/__init__.py")
else:
    print("ℹ️ already exists: apps/suppliers/urls/__init__.py")
