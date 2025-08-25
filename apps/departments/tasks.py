# ERP_CORE/departments/tasks.py

from celery import shared_task
from .models import Department
from apps.employees.models import Employee

@shared_task
def notify_managers_on_new_employees():
    """
    مهمة ترسل إشعارًا تلقائيًا عند انضمام موظف جديد إلى قسم معين.
    """
    departments = Department.objects.all()
    for department in departments:
        new_employees = Employee.objects.filter(department=department, hire_date__gte='2025-01-01')
        if new_employees.exists():
            # هنا يمكن إرسال إشعار أو إيميل للمدير
            pass
