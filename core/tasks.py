# ERP_CORE/core/tasks.py

from celery import shared_task
from .ai import detect_missing_configurations

@shared_task
def run_core_ai_checks():
    """
    مهمة مجدولة لتفعيل فحص إعدادات CORE وتنبيه النظام الذكي.
    """
    detect_missing_configurations()
