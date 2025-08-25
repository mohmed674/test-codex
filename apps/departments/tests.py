# ERP_CORE/departments/tests.py
from django.test import TestCase
from django.urls import reverse
from .models import Department

class DepartmentModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="الإنتاج", description="قسم الإنتاج")

    def test_str_representation(self):
        self.assertEqual(str(self.dept), "الإنتاج")

    def test_default_is_active(self):
        self.assertTrue(self.dept.is_active)

    def test_slug_nullable(self):
        self.assertIsNone(self.dept.slug)

class DepartmentViewsTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="الجودة", description="قسم الجودة")

    def test_list_view(self):
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "قسم الجودة")

    def test_create_view(self):
        response = self.client.post(reverse('department_create'), {
            'name': 'الموارد البشرية',
            'description': 'قسم الموارد'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Department.objects.filter(name='الموارد البشرية').exists())

    def test_edit_view(self):
        response = self.client.post(reverse('department_edit', args=[self.dept.id]), {
            'name': 'الجودة والتفتيش',
            'description': 'تم التحديث'
        })
        self.assertEqual(response.status_code, 302)
        self.dept.refresh_from_db()
        self.assertEqual(self.dept.name, 'الجودة والتفتيش')

    def test_delete_view(self):
        response = self.client.post(reverse('department_delete', args=[self.dept.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Department.objects.filter(id=self.dept.id).exists())
