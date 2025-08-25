from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'dashboard_center'

urlpatterns = [
    # /dashboard/ → إعادة توجيه أنظف لمسار أوفرڤيو
    path('', RedirectView.as_view(pattern_name='dashboard_center:overview', permanent=False)),
    # /dashboard/overview/ → لوحة الـ KPIs + الرسم
    path('overview/', views.main_dashboard, name='overview'),
]
