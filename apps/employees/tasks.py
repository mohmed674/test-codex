# apps/employees/tasks.py
from __future__ import annotations

import logging
from typing import Any

import requests
from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.timezone import now
from weasyprint import HTML

from apps.employees.models import Employee, MonthlyIncentive
from apps.employees.utils.logic import calculate_employee_rewards

LOG = logging.getLogger("employees.tasks")


@shared_task
def run_monthly_incentive_calculation() -> None:
    """
    يُشغِّل حساب الحوافز والخصومات لكل الموظفين في بداية الشهر،
    ويُنتِج تقرير PDF ويُرسل إشعارات بالبريد (واختياريًا عبر WhatsApp).
    """
    today = now().date().replace(day=1)

    employees_qs = Employee.objects.filter(active=True)
    for employee in employees_qs:
        calculate_employee_rewards(employee, month=today)

    # توليد تقرير PDF شامل
    context: dict[str, Any] = {
        "records": MonthlyIncentive.objects.filter(month=today),
        "month": today,
    }
    html_string: str = render_to_string(
        "employees/monthly_incentive_report.html", context
    )
    pdf_bytes = HTML(string=html_string).write_pdf()
    if pdf_bytes is None:
        pdf_bytes = b""

    # حفظه في media/reports
    filename = f"monthly_incentives_{today.strftime('%Y_%m')}.pdf"
    path = f"reports/{filename}"
    default_storage.save(path, ContentFile(bytes(pdf_bytes)))

    # إشعار بالبريد
    subject = f"📊 تقرير الحوافز والخصومات لشهر {today.strftime('%m/%Y')}"
    message = (
        f"تم حساب الحوافز والخصومات بنجاح لـ {employees_qs.count()} موظفًا ✅\n\n"
        f"📁 التقرير تم حفظه في media/reports/{filename}\n"
        f"📅 التاريخ: {today.strftime('%Y-%m-%d')}\n"
        "📌 يمكنك مراجعة التفاصيل عبر لوحة الإدارة أو الملف الشخصي لكل موظف."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        ["hr@yourcompany.com", "manager@yourcompany.com"],
        fail_silently=False,
    )

    # إشعار WhatsApp (اختياري)
    try:
        whatsapp_payload = {
            "token": settings.WHATSAPP_API_TOKEN,
            "to": settings.WHATSAPP_TO,
            "body": (
                f"📢 تم احتساب الحوافز لـ {employees_qs.count()} موظفًا "
                f"في {today.strftime('%m/%Y')}.\n"
                f"📁 التقرير متوفر في media/reports/{filename}"
            ),
        }
        requests.post(settings.WHATSAPP_API_URL, data=whatsapp_payload, timeout=10)
    except requests.RequestException as exc:
        LOG.warning(
            "WhatsApp notify failed: %s", exc, extra={"event": "whatsapp_failed"}
        )
