from pathlib import Path

BASE = Path(__file__).resolve().parent
urls_pkg = BASE / "apps" / "suppliers" / "urls"
urls_pkg.mkdir(parents=True, exist_ok=True)

# 1) تأكيد أن main.py يعرّف urlpatterns
main_py = urls_pkg / "main.py"
if not main_py.exists():
    main_py.write_text(
        "from django.urls import path, include\n"
        "urlpatterns = [\n"
        "    path('api/', include('apps.suppliers.urls.api')),\n"
        "]\n",
        encoding="utf-8",
    )
else:
    txt = main_py.read_text(encoding="utf-8")
    if "urlpatterns" not in txt:
        txt += "\nfrom django.urls import path, include\nurlpatterns = [path('api/', include('apps.suppliers.urls.api'))]\n"
        main_py.write_text(txt, encoding="utf-8")

# 2) اجعل __init__.py يصدّر urlpatterns من main
init_py = urls_pkg / "__init__.py"
init_py.write_text("from .main import urlpatterns\n", encoding="utf-8")

print("✅ suppliers urls export restored (apps/suppliers/urls/__init__.py → urlpatterns)")
