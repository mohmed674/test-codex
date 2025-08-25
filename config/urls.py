# config/urls.py
# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # تعدد اللغات (لأجل set_language)
    path('i18n/', include('django.conf.urls.i18n')),

    # الواجهة الأساسية
    path('', include('core.urls')),

    # Websites / Site
    path('site/', include('apps.site.urls')),

    # التطبيقات (apps/)
    path('accounting/', include('apps.accounting.urls')),
    path('ai_decision/', include('apps.ai_decision.urls')),
    path('api_gateway/', include('apps.api_gateway.urls')),
    path('asset_lifecycle/', include('apps.asset_lifecycle.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('audit_out/', include('apps.audit_out.urls')),
    path('backup_center/', include('apps.backup_center.urls')),
    path('bi/', include('apps.bi.urls')),
    path('campaigns/', include('apps.campaigns.urls')),
    path('clients/', include('apps.clients.urls')),
    path('client_portal/', include('apps.client_portal.urls')),
    path('communication/', include('apps.communication.urls')),
    path('contracts/', include('apps.contracts.urls')),
    path('crm/', include('apps.crm.urls')),
    path('dark_mode/', include('apps.dark_mode.urls')),
    path('dashboard_center/', include('apps.dashboard_center.urls')),
    path('demand_forecasting/', include('apps.demand_forecasting.urls')),
    path('departments/', include('apps.departments.urls')),
    path('discipline/', include('apps.discipline.urls')),
    path('docs/', include('apps.docs.urls')),
    path('document_center/', include('apps.document_center.urls')),
    path('employees/', include('apps.employees.urls')),
    path('employee_monitoring/', include('apps.employee_monitoring.urls')),
    path('evaluation/', include('apps.evaluation.urls')),
    path('expenses/', include('apps.expenses.urls')),
    path('internal_bot/', include('apps.internal_bot.urls')),
    path('internal_monitoring/', include('apps.internal_monitoring.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('knowledge_center/', include('apps.knowledge_center.urls')),
    path('legal/', include('apps.legal.urls')),
    path('maintenance/', include('apps.maintenance.urls')),
    path('media/', include('apps.media.urls')),
    path('mobile/', include('apps.mobile.urls')),
    path('monitoring/', include('apps.monitoring.urls')),
    path('mrp/', include('apps.mrp.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('offline_sync/', include('apps.offline_sync.urls')),
    path('pattern/', include('apps.pattern.urls')),
    path('payroll/', include('apps.payroll.urls')),
    path('plm/', include('apps.plm.urls')),
    path('pos/', include('apps.pos.urls')),
    path('production/', include('apps.production.urls')),
    path('products/', include('apps.products.urls')),
    path('projects/', include('apps.projects.urls')),
    path('purchases/', include('apps.purchases.urls')),
    path('qms/', include('apps.qms.urls')),
    path('recruitment/', include('apps.recruitment.urls')),
    path('rfq/', include('apps.rfq.urls')),
    path('risk_management/', include('apps.risk_management.urls')),
    path('sales/', include('apps.sales.urls')),
    path('shipping/', include('apps.shipping.urls')),
    path('suppliers/', include('apps.suppliers.urls')),
    path('support/', include('apps.support.urls')),
    path('survey/', include('apps.survey.urls')),
    path('templates/', include('apps.templates.urls')),
    path('themes/', include('apps.themes.urls')),
    path('theme_manager/', include('apps.theme_manager.urls')),
    path('tracking/', include('apps.tracking.urls')),
    path('vendor_portal/', include('apps.vendor_portal.urls')),
    path('voice_commands/', include('apps.voice_commands.urls')),
    path('warehouse_map/', include('apps.warehouse_map.urls')),
    path('whatsapp_bot/', include('apps.whatsapp_bot.urls')),
    path('workflow/', include('apps.workflow.urls')),
    path('work_regulations/', include('apps.work_regulations.urls')),

    # New: Banking integration
    path('banking/', include('apps.banking.urls')),
]

# خدمة الملفات الثابتة والوسائط أثناء التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
