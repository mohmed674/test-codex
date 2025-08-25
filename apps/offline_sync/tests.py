from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import OfflineSyncLog
from django.utils import timezone

class OfflineSyncModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_offline_sync_log(self):
        log = OfflineSyncLog.objects.create(user=self.user, data_summary='Test sync data')
        self.assertEqual(str(log), f"Sync by {self.user.username} at {log.synced_at.strftime('%Y-%m-%d %H:%M')}")

class OfflineSyncViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        OfflineSyncLog.objects.create(user=self.user, data_summary='Initial sync')

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('offline_sync:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_view(self):
        response = self.client.get(reverse('offline_sync:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'لوحة تحكم المزامنة دون اتصال')
        self.assertContains(response, 'Initial sync')
