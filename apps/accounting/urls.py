# D:\ERP_CORE\accounting\urls.py
from django.urls import path, include
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter

from . import views
from . import invoice_views
from .report_views import payments_by_method_report

router = DefaultRouter()
router.register(r'supplier-invoices', views.SupplierInvoiceViewSet, basename='supplier-invoice')

app_name = 'accounting'

urlpatterns = [
    path('', views.home, name='list'),
    path('index/', views.home, name='index'),

    # ========== فواتير المبيعات ==========
    path('sales/create/', invoice_views.create_sales_invoice, name='create_sales_invoice'),
    path('sales/<int:pk>/', invoice_views.sales_invoice_detail, name='sales_invoice_detail'),
    path('sales/', invoice_views.sales_invoice_dashboard, name='sales_invoice_dashboard'),
    path('sales/export/excel/', invoice_views.sales_invoice_excel, name='sales_invoice_excel'),

    # ========== فواتير المشتريات ==========
    path('purchase/create/', invoice_views.create_purchase_invoice, name='create_purchase_invoice'),
    path('purchase/<int:pk>/', invoice_views.purchase_invoice_detail, name='purchase_invoice_detail'),

    # ========== طباعة PDF ==========
    path('invoice/<str:invoice_type>/<int:pk>/print/', invoice_views.print_invoice_pdf, name='print_invoice_pdf'),

    # ========== قيود اليومية ==========
    path('journal/', views.journal_dashboard, name='journal_dashboard'),
    path('journal/create/', views.journal_create, name='journal_create'),
    path('journal/ai/create/', views.journal_entry_create_view, name='journal_entry_create'),
    path('journal/<int:pk>/', views.journal_detail, name='journal_detail'),

    # ========== الشركاء ==========
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),

    # ========== المنتجات (إحالة للـ products) ==========
    path('products/', RedirectView.as_view(url='/products/', permanent=True, query_string=True), name='product_list'),
    path('products/create/', RedirectView.as_view(url='/products/create/', permanent=True, query_string=True), name='product_create'),

    # ========== تقارير وتصدير عام ==========
    path('export/excel/', views.export_accounting_excel, name='export_accounting_excel'),
    path('export/pdf/', views.export_accounting_pdf, name='export_accounting_pdf'),
    path('export/csv/', views.export_accounting_csv, name='export_accounting_csv'),

    path('reports/', views.reports_overview_view, name='reports_overview'),
    path('reports/payments-method/', payments_by_method_report, name='payments_by_method_report'),
    path('analysis/financial/', views.financial_analysis_view, name='financial_analysis'),

    # ========== ذكاء محاسبي ==========
    path('ai-guided-entry/', views.guided_journal_entry_view, name='ai_guided_entry'),
    path('suggestions/', views.suggestion_log_view, name='accounting_suggestions'),

    # ========== API ==========
    path('api/', include(router.urls)),
]
