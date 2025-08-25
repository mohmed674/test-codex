import pytest
from django.apps import apps
from django.db import connection


@pytest.mark.django_db
def test_employees_tables_exist_after_migrate():
    """
    التأكد من أن جداول employees الأساسية موجودة بعد الميجريشن.
    """
    existing = set(connection.introspection.table_names())
    expected = {
        "employees_employee",       # جدول الموظفين
        "employees_department",     # جدول الأقسام
    }
    missing = [t for t in expected if t not in existing]
    assert not missing, f"Employees tables missing: {missing}"


def test_employees_app_is_installed():
    """
    التحقق من أن تطبيق employees مُسجَّل في INSTALLED_APPS.
    """
    installed = {cfg.name for cfg in apps.get_app_configs()}
    assert "employees" in installed, "employees app is not installed"


@pytest.mark.django_db
def test_create_employee_and_department():
    """
    تجربة إنشاء قسم وموظف للتأكد من أن العلاقات الأساسية تعمل.
    """
    Department = apps.get_model("employees", "Department")
    Employee = apps.get_model("employees", "Employee")

    dept = Department.objects.create(name="الإدارة")
    emp = Employee.objects.create(name="أحمد", department=dept)

    assert Department.objects.count() == 1
    assert Employee.objects.count() == 1
    assert emp.department.name == "الإدارة"
