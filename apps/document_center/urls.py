from django.urls import path
from . import views

app_name = 'document_center'

urlpatterns = [
    path('', views.document_upload, name='upload'),
    # ❌ تعليق السطر التالي لأنه غير موجود حاليًا
    # path('approvals/', views.document_approvals, name='approvals'),
]
