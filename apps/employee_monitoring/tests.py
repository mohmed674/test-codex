from django.test import TestCase
from django.utils import timezone
from apps.employees.models import Employee
from .models import MonitoringRecord

class MonitoringRecordTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            name='Test Employee',
            job_title='Operator',
            department=None
        )

    def test_monitoring_record_creation(self):
        record = MonitoringRecord.objects.create(
            employee=self.employee,
            status='present',
            notes='Test attendance'
        )
        self.assertEqual(record.status, 'present')
        self.assertEqual(record.notes, 'Test attendance')
        self.assertEqual(record.employee.name, 'Test Employee')
        self.assertEqual(str(record), f"{self.employee.name} - {record.date} - {record.status}")
