# notifications/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationViewSet,
    notification_list,
    mark_as_read,
    export_notifications_pdf,
    export_notifications_excel,
)

app_name = "notifications"

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # واجهة الويب
    path('', notification_list, name='list'),
    path('<int:pk>/read/', mark_as_read, name='mark_as_read'),
    path('export/pdf/', export_notifications_pdf, name='export_pdf'),
    path('export/excel/', export_notifications_excel, name='export_excel'),

    # REST API
    path('api/', include(router.urls)),
]
