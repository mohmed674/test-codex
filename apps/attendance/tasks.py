# ERP_CORE/attendance/tasks.py

from celery import shared_task
from .models import Attendance  # ✅ هذا هو الموديل الصحيح

from apps.employees.models import Employee
from django.utils.timezone import now
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def auto_mark_absentees():
    """
    مهمة ذكية يومية لوضع غياب تلقائي للموظفين غير المسجلين.
    """
    today = now().date()
    all_employees = set(Employee.objects.values_list('id', flat=True))
    present_today = set(Attendance.objects.filter(date=today).values_list('employee_id', flat=True))
    absent_ids = all_employees - present_today

    records = []
    for emp_id in absent_ids:
        records.append(Attendance(
            employee_id=emp_id,
            date=today,
            status='absent',
            notes='تم تسجيل غياب تلقائيًا'
        ))

    Attendance.objects.bulk_create(records)
    logger.info(f"✅ تم تسجيل {len(records)} غياب تلقائي لليوم {today}")
