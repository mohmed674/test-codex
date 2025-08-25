# ERP_CORE/core/api_urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'job-titles', api_views.JobTitleViewSet)
router.register(r'units', api_views.UnitViewSet)
router.register(r'evaluation-criteria', api_views.EvaluationCriteriaViewSet)
router.register(r'stage-types', api_views.ProductionStageTypeViewSet)
router.register(r'risk-thresholds', api_views.RiskThresholdViewSet)
router.register(r'department-roles', api_views.DepartmentRoleViewSet)

urlpatterns = router.urls
