from django.urls import path
from . import views

app_name = 'vendor_portal'

urlpatterns = [
    path('', views.portal_home, name='list'),
    # ❌ حذف السطر التالي مؤقتًا لأنه مسبب للكسر
    # path('create/', views.create_vendor, name='create'),
]
