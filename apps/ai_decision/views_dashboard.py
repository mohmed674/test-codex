from __future__ import annotations

from datetime import timedelta

from django.apps import apps as django_apps
from django.db.models import Count, Exists, F, OuterRef
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _


def _get_model(app_label: str, model_name: str):
    """Lazy, safe model fetch. Returns None if not installed/renamed."""
    try:
        return django_apps.get_model(app_label, model_name)
    except (LookupError, ValueError):
        return None


# ✅ 1) لوحة القيادة الذكية
def ai_dashboard(request):
    today = timezone.now().date()
    alerts: list[str] = []
    suggestions: list[str] = []

    Attendance = _get_model("attendance", "Attendance")
    ProductionLog = _get_model("production", "ProductionLog")
    Deduction = _get_model("payroll", "Deduction")
    MachineLog = _get_model("maintenance", "MachineLog")

    # 🔴 غياب متكرر
    if Attendance is not None:
        absence_agg = (
            Attendance.objects.filter(status="absent", date__gte=today.replace(day=1))
            .values("employee__name")
            .annotate(total=Count("id"))
            .filter(total__gte=3)
        )
        for abs_ in absence_agg:
            alerts.append(
                _("🔴 الموظف {name} غاب {days} أيام هذا الشهر.").format(
                    name=abs_["employee__name"],
                    days=abs_["total"],
                )
            )

        if absence_agg.exists():
            suggestions.append(_("🔧 يوصى بإرسال إنذار رسمي للموظفين كثيري الغياب."))

    # 🟠 إنتاجية منخفضة
    if ProductionLog is not None:
        low_production = (
            ProductionLog.objects.values("employee__name")
            .annotate(total=Count("id"))
            .filter(total__lt=10)
        )
        for prod in low_production:
            alerts.append(
                _("🟠 إنتاجية {name} منخفضة ({count} قطعة فقط).").format(
                    name=prod["employee__name"],
                    count=prod["total"],
                )
            )
        if low_production.exists():
            suggestions.append(
                _("📈 ينصح بإعادة توزيع المهام أو تحفيز العمال ضعيفي الإنتاج.")
            )

    # 🟠 خصومات كثيرة
    if Deduction is not None:
        high_deductions = (
            Deduction.objects.filter(date__month=today.month)
            .values("employee__name")
            .annotate(total=Count("id"))
            .filter(total__gt=5)
        )
        for ded in high_deductions:
            alerts.append(
                _("🟠 الموظف {name} حصل على {count} خصومات هذا الشهر.").format(
                    name=ded["employee__name"],
                    count=ded["total"],
                )
            )
        if high_deductions.exists():
            suggestions.append(
                _("⛔ راجع أسباب الخصومات المتكررة فقد تكون مؤشرًا لمشكلة " "إدارية.")
            )

    # ⚠️ صيانة متكررة
    if MachineLog is not None:
        frequent_maintenance = (
            MachineLog.objects.filter(date__month=today.month)
            .values("machine__name")
            .annotate(total=Count("id"))
            .filter(total__gt=3)
        )
        for log in frequent_maintenance:
            alerts.append(
                _("⚠️ الماكينة {name} توقفت {count} مرة هذا الشهر.").format(
                    name=log["machine__name"],
                    count=log["total"],
                )
            )
        if frequent_maintenance.exists():
            suggestions.append(_("🔍 راجع الصيانة الدورية للماكينات."))

    return render(
        request,
        "ai_decision/dashboard.html",
        {"alerts": alerts, "suggestions": suggestions, "date": today},
    )


# ✅ 2) لوحة تقارير تحليل المنتجات الراكدة والخاسرة
def ai_reports_dashboard(request):
    Product = _get_model("products", "Product")
    SalesOrder = _get_model("sales", "SalesOrder")

    stale_products = 0
    loss_count = 0

    if Product is not None:
        # منتج راكد: لا توجد أوامر بيع مرتبطة خلال آخر 60 يومًا
        sixty_days_ago = timezone.now() - timedelta(days=60)
        if SalesOrder is not None:
            has_recent_sales = SalesOrder.objects.filter(
                product=OuterRef("pk"),
                created_at__gte=sixty_days_ago,
            )
            stale_products = (
                Product.objects.annotate(has_recent=Exists(has_recent_sales))
                .filter(has_recent=False)
                .count()
            )
        # منتجات تُباع بخسارة (يتطلب الحقول المعروفة)
        try:
            loss_count = Product.objects.filter(
                selling_price__lt=F("cost_price")
            ).count()
        except Exception:
            loss_count = 0

    recommendation_parts: list[str] = []
    if stale_products > 0:
        recommendation_parts.append(
            _(
                "📉 يوجد {count} منتج راكد، يُفضل مراجعة خطة التوزيع "
                "أو الإيقاف المؤقت."
            ).format(count=stale_products)
        )
    if loss_count > 0:
        recommendation_parts.append(
            _(
                "💸 هناك {count} منتج يتم بيعه بخسارة، يُنصح بتعديل الأسعار "
                "أو تقليل التكاليف."
            ).format(count=loss_count)
        )
    recommendation = " ".join(recommendation_parts)

    return render(
        request,
        "ai_decision/reports_dashboard.html",
        {
            "stale_products": stale_products,
            "loss_count": loss_count,
            "recommendation": recommendation,
        },
    )


# ✅ 3) تحليل مبيعات AI (حسب المدة)
def ai_sales_analysis_report(request):
    AIDecisionAlert = _get_model("ai_decision", "AIDecisionAlert")
    mode = request.GET.get("mode", "daily")
    now = timezone.now()

    since = {
        "daily": now - timedelta(days=1),
        "weekly": now - timedelta(days=7),
        "monthly": now - timedelta(days=30),
    }.get(mode, now - timedelta(days=1))

    alerts = ()
    if AIDecisionAlert is not None:
        alerts = AIDecisionAlert.objects.filter(
            section="sales",
            created_at__gte=since,
        ).order_by("-created_at")

    return render(
        request,
        "ai_decision/sales_analysis_report.html",
        {"alerts": alerts, "mode": mode},
    )


# ✅ 4) لوحة التعلم الذاتي من البيانات المستقبلية
def ai_learning_dashboard(request):
    try:
        from apps.ai_decision.learning.adaptive_learning import \
            analyze_recent_decisions
    except Exception:
        patterns = []
    else:
        patterns = analyze_recent_decisions()

    return render(request, "ai_decision/dashboard.html", {"patterns": patterns})
