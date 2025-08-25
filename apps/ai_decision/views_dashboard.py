from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Sum, F
from datetime import timedelta

from apps.attendance.models import Attendance
from apps.payroll.models import Deduction
from apps.production.models import ProductionLog
from apps.maintenance.models import MachineLog
from apps.products.models import Product
from apps.sales.models import SalesOrder
from apps.ai_decision.models import AIDecisionAlert

# ✅ 1. لوحة القيادة الذكية AI Dashboard
def ai_dashboard(request):
    today = timezone.now().date()
    alerts, suggestions = [], []

    # 🔴 غياب متكرر
    absence_agg = Attendance.objects.filter(
        status='absent', date__gte=today.replace(day=1)
    ).values('employee__name').annotate(total=Count('id')).filter(total__gte=3)

    for abs in absence_agg:
        alerts.append(f"🔴 الموظف {abs['employee__name']} غاب {abs['total']} أيام هذا الشهر.")

    # 🟠 إنتاجية منخفضة
    low_production = ProductionLog.objects.values('employee__name')\
        .annotate(total=Count('id')).filter(total__lt=10)
    for prod in low_production:
        alerts.append(f"🟠 إنتاجية {prod['employee__name']} منخفضة ({prod['total']} قطعة فقط).")

    # 🟠 خصومات كثيرة
    high_deductions = Deduction.objects.filter(date__month=today.month)\
        .values('employee__name').annotate(total=Count('id')).filter(total__gt=5)
    for ded in high_deductions:
        alerts.append(f"🟠 الموظف {ded['employee__name']} حصل على {ded['total']} خصومات هذا الشهر.")

    # ⚠️ صيانة متكررة
    frequent_maintenance = MachineLog.objects.filter(date__month=today.month)\
        .values('machine__name').annotate(total=Count('id')).filter(total__gt=3)
    for log in frequent_maintenance:
        alerts.append(f"⚠️ الماكينة {log['machine__name']} توقفت {log['total']} مرة هذا الشهر.")

    # 🧐 اقتراحات ذكية
    if absence_agg.exists():
        suggestions.append("🔧 يوصى بإرسال إنذار رسمي للموظفين كثيري الغياب.")
    if low_production.exists():
        suggestions.append("📈 ينصح بإعادة توزيع المهام أو تحفيز العمال ضعيفي الإنتاج.")
    if high_deductions.exists():
        suggestions.append("⛔ راجع أسباب الخصومات المتكررة فقد تكون مؤشرًا لمشكلة إدارية.")
    if frequent_maintenance.exists():
        suggestions.append("🔍 راجع الصيانة الدورية للماكينات.")

    return render(request, 'ai_decision/dashboard.html', {
        'alerts': alerts,
        'suggestions': suggestions,
        'date': today
    })


# ✅ 2. لوحة تقارير تحليل المنتجات الراكدة والخاسرة
def ai_reports_dashboard(request):
    stale_products = Product.objects.annotate(
        total_sales=Sum('salesorder__quantity', filter=(
            SalesOrder.objects.filter(created_at__gte=timezone.now() - timedelta(days=60))
        ))
    ).filter(total_sales__isnull=True).count()

    loss_count = Product.objects.filter(selling_price__lt=F('cost_price')).count()

    recommendation = ""
    if stale_products > 0:
        recommendation += f"📉 يوجد {stale_products} منتج راكد، يُفضل مراجعة خطة التوزيع أو الإيقاف المؤقت. "
    if loss_count > 0:
        recommendation += f"💸 هناك {loss_count} منتج يتم بيعه بخسارة، يُنصح بتعديل الأسعار أو تقليل التكاليف."

    return render(request, 'ai_decision/reports_dashboard.html', {
        'stale_products': stale_products,
        'loss_count': loss_count,
        'recommendation': recommendation
    })


# ✅ 3. تحليل مبيعات AI (حسب المدة)
def ai_sales_analysis_report(request):
    mode = request.GET.get('mode', 'daily')
    now = timezone.now()

    since = {
        'daily': now - timedelta(days=1),
        'weekly': now - timedelta(days=7),
        'monthly': now - timedelta(days=30),
    }.get(mode, now - timedelta(days=1))

    alerts = AIDecisionAlert.objects.filter(
        section='sales',
        created_at__gte=since
    ).order_by('-created_at')

    return render(request, 'ai_decision/sales_analysis_report.html', {
        'alerts': alerts,
        'mode': mode,
    })


# ✅ 4. لوحة التعلم الذاتي من البيانات المستقبلية
from apps.ai_decision.learning.adaptive_learning import analyze_recent_decisions

def ai_learning_dashboard(request):
    patterns = analyze_recent_decisions()
    return render(request, 'ai_decision/dashboard.html', {'patterns': patterns})
