# ERP_CORE/ERP_CORE/urls.py
import importlib

from django.conf import settings
from django.conf.urls.static import static as serve_static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic.base import RedirectView
from django.views.i18n import set_language as dj_set_language

from core.views_pwa import manifest_json, service_worker

urlpatterns = [
    # PLM
    path('plm/', include(('apps.plm.urls', 'plm'), namespace='plm')),

    # Core
    path('', include(('core.urls', 'core'), namespace='core')),
    path('admin/', admin.site.urls),

    # PWA
    path('manifest.json', manifest_json, name='manifest_json'),
    path('sw.js', service_worker, name='service_worker'),

    # Favicon
    path(
        'favicon.ico',
        RedirectView.as_view(
            url=staticfiles_storage.url('icons/icon-192x192.png'),
            permanent=True
        ),
        name='favicon'
    ),
]

# إضافة تلقائية لباقي التطبيقات (بدون plm)
apps_with_urls = [
    'employees', 'attendance', 'evaluation', 'departments', 'payroll',
    'discipline', 'employee_monitoring', 'production', 'pattern', 'products',
    'inventory', 'accounting', 'ai_decision', 'voice_commands', 'tracking',
    'survey', 'maintenance', 'monitoring', 'internal_monitoring', 'sales',
    'whatsapp_bot', 'clients', 'media', 'bi', 'campaigns', 'client_portal',
    'contracts', 'crm', 'legal', 'mobile', 'notifications', 'offline_sync',
    'pos', 'projects', 'purchases', 'risk_management', 'shipping', 'suppliers',
    'support', 'api_gateway', 'asset_lifecycle', 'backup_center', 'communication',
    'dashboard_center', 'demand_forecasting', 'document_center', 'expenses',
    'internal_bot', 'knowledge_center', 'recruitment', 'rfq', 'vendor_portal',
    'warehouse_map', 'work_regulations', 'workflow', 'theme_manager', 'dark_mode',
]

for app in apps_with_urls:
    try:
        importlib.import_module(f"apps.{app}.urls")
        urlpatterns.append(
            path(f'{app.replace("_", "-")}/', include((f'apps.{app}.urls', app), namespace=app))
        )
    except ModuleNotFoundError:
        pass

# i18n
urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', dj_set_language, name='set_language'),
]

# ملفات الميديا والستاتيك
if settings.DEBUG:
    urlpatterns += serve_static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
