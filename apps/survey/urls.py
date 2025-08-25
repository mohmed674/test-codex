from django.urls import path
from . import views

app_name = 'survey'

urlpatterns = [
    path('<int:survey_id>/', views.take_survey, name='take_survey'),
    path('thanks/', views.thanks, name='thanks'),

    # ✅ عرض نتائج استبيان
    path('<int:survey_id>/results/', views.survey_results, name='survey_results'),

    # ✅ تصدير PDF
    path('<int:survey_id>/export/pdf/', views.export_survey_pdf, name='export_survey_pdf'),

    # ✅ تصدير Excel
    path('<int:survey_id>/export/excel/', views.export_survey_excel, name='export_survey_excel'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
