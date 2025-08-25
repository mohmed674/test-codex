from django.db import models
from django.contrib.auth.models import User

TRIGGER_EVENTS = [
    ('on_create', 'عند الإنشاء'),
    ('on_update', 'عند التعديل'),
    ('on_status_change', 'عند تغيير الحالة'),
]

ACTION_TYPES = [
    ('send_email', 'إرسال بريد'),
    ('change_status', 'تغيير حالة'),
    ('notify_user', 'تنبيه مستخدم'),
    ('assign_task', 'إسناد مهمة'),
]

class WorkflowRule(models.Model):
    name = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100)  # ex: PurchaseOrder
    trigger_event = models.CharField(max_length=50, choices=TRIGGER_EVENTS)
    condition_field = models.CharField(max_length=100)
    condition_value = models.CharField(max_length=100)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_value = models.CharField(max_length=255, help_text="مثل: الحالة الجديدة، المستخدم المستهدف...")

    def __str__(self):
        return self.name
