"""
WSGI config for ERP_CORE project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments.

It exposes a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

# ضبط متغير البيئة الخاص بإعدادات المشروع
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ERP_CORE.settings')

# استيراد تطبيق WSGI لتشغيل المشروع
application = get_wsgi_application()
