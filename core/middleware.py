# core/middleware.py
from datetime import timedelta

from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from apps.internal_monitoring.models import (InventoryDiscrepancy,
                                             SuspiciousActivity)


class MonitoringAlertMiddleware(MiddlewareMixin):
    """
    يُظهر تنبيهات سريعة للمستخدمين المسجَّلين عن:
      - وجود عجز مخزني غير محلول
      - وجود أنشطة مشبوهة خلال آخر 48 ساعة غير محلولة
    الرسائل ملفوفة بـ gettext_lazy لضمان الترجمة حسب اللغة المختارة.
    """

    def process_request(self, request):
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return

        # تنبيه بوجود عجز مخزني غير محلول
        if InventoryDiscrepancy.objects.filter(resolved=False).exists():
            messages.warning(request, _("⚠️ يوجد عجز مخزني جاري التحقيق فيه!"))

        # تنبيه بوجود نشاط مشبوه خلال آخر 48 ساعة غير محلول
        recent_activities = SuspiciousActivity.objects.filter(
            timestamp__gte=now() - timedelta(hours=48), resolved=False
        )
        if recent_activities.exists():
            messages.error(
                request, _("🚨 تم رصد أنشطة مشبوهة مؤخرًا، راجع المراقبة الذكية.")
            )


class NoCacheHTMLMiddleware(MiddlewareMixin):
    """
    يمنع تخزين صفحات HTML في الكاش لضمان أن تغيير اللغة يظهر فورًا،
    ويضيف ترويسات Vary على Cookie و Accept-Language.
    """

    def process_response(self, request, response):
        content_type = response.get("Content-Type", "")
        if "text/html" in content_type:
            # لا كاش على HTML
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

            # الرد يتأثر باللغة المختارة وكوكي الجلسة
            vary_existing = response.get("Vary", "")
            vary_set = {v.strip() for v in vary_existing.split(",") if v.strip()}
            vary_set.update({"Cookie", "Accept-Language"})
            response["Vary"] = ", ".join(sorted(vary_set))

        return response
