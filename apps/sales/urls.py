from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # ✅ لوحة المبيعات والتحليلات
    path('dashboard/', views.sales_dashboard_view, name='dashboard'),

    # ✅ عمليات البيع والفواتير
    path('invoices/', views.invoice_list_view, name='invoice_list'),
    path('invoices/create/', views.invoice_create_view, name='invoice_create'),

    # ✅ أداء المبيعات وتحليل مندوبي البيع
    path('performance/', views.performance_view, name='performance'),

    # ✅ توصيات الذكاء الاصطناعي
    path('suggestions/', views.smart_suggestions_view, name='suggestions'),

    # ✅ طباعة الفواتير
    path('invoice/<int:invoice_id>/print/', views.print_invoice, name='invoice_print'),
    path('invoice/<int:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),

    # ✅ إنشاء عملية بيع سريعة مع تنبيه ذكي
    path('create-sale/', views.create_sale, name='create_sale'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
