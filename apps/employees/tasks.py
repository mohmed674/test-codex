from celery import shared_task
from django.utils.timezone import now
from apps.employees.models import Employee, MonthlyIncentive
from apps.employees.utils.logic import calculate_employee_rewards
from django.core.mail import send_mail
from django.conf import settings
import requests

# ✅ لإنتاج PDF
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


@shared_task
def run_monthly_incentive_calculation():
    """
    يتم تشغيل هذه المهمة تلقائيًا في بداية كل شهر
    لحساب الحوافز والخصومات لجميع الموظفين.
    """
    today = now().date().replace(day=1)
    employees = Employee.objects.filter(active=True)
    for employee in employees:
        calculate_employee_rewards(employee, month=today)

    # ✅ توليد تقرير PDF شامل
    context = {
        'records': MonthlyIncentive.objects.filter(month=today),
        'month': today,
    }
    html_string = render_to_string('employees/monthly_incentive_report.html', context)
    pdf_file = HTML(string=html_string).write_pdf()

    # ✅ حفظه في media/reports
    filename = f"monthly_incentives_{today.strftime('%Y_%m')}.pdf"
    path = f"reports/{filename}"
    default_storage.save(path, ContentFile(pdf_file))

    # ✅ إشعار بالبريد
    subject = f'📊 تقرير الحوافز والخصومات لشهر {today.strftime("%m/%Y")}'
    message = (
        f"تم حساب الحوافز والخصومات بنجاح لـ {employees.count()} موظفًا ✅\n\n"
        f"📁 التقرير تم حفظه في media/reports/{filename}\n"
        f"📅 التاريخ: {today.strftime('%Y-%m-%d')}\n"
        "📌 يمكنك مراجعة التفاصيل عبر لوحة الإدارة أو الملف الشخصي لكل موظف."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        ['hr@yourcompany.com', 'manager@yourcompany.com'],  # ✏️ غيّر العناوين
        fail_silently=False,
    )

    # ✅ إشعار WhatsApp (اختياري)
    try:
        whatsapp_payload = {
            "token": settings.WHATSAPP_API_TOKEN,
            "to": settings.WHATSAPP_TO,
            "body": f"📢 تم احتساب الحوافز لـ {employees.count()} موظفًا في {today.strftime('%m/%Y')}.\n📁 التقرير متوفر في media/reports/{filename}"
        }
        requests.post(settings.WHATSAPP_API_URL, data=whatsapp_payload)
    except Exception as e:
        print(f"⚠️ فشل إرسال WhatsApp: {e}")
