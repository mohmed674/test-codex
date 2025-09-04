from __future__ import annotations

# نقطة الدخول الوحيدة لروابط الموردين
# نتأكد إنها تصدّر urlpatterns من الملفات الداخلية
from .main import urlpatterns  # noqa: F401
