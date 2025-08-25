from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('', views.campaign_list, name='campaign_list'),
    path('create/', views.create_campaign, name='create'),
    path('<int:pk>/', views.campaign_detail, name='detail'),
    # ❌ حذف السطر التالي مؤقتًا حتى يتم تنفيذ الدالة
    # path('send/email/', views.send_email_campaign, name='send_email'),
]
