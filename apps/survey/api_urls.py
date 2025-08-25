# survey/api_urls.py

from django.urls import path
from . import api_views

urlpatterns = [
    path('list/', api_views.SurveyListAPI.as_view(), name='api_survey_list'),
    path('submit/', api_views.SubmitSurveyAPI.as_view(), name='api_survey_submit'),
]
