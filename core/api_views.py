# ERP_CORE/core/api_views.py

from rest_framework import viewsets

from .models import (DepartmentRole, EvaluationCriteria, JobTitle,
                     ProductionStageType, RiskThreshold, Unit)
from .serializers import (DepartmentRoleSerializer,
                          EvaluationCriteriaSerializer, JobTitleSerializer,
                          ProductionStageTypeSerializer,
                          RiskThresholdSerializer, UnitSerializer)


class JobTitleViewSet(viewsets.ModelViewSet):
    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class EvaluationCriteriaViewSet(viewsets.ModelViewSet):
    queryset = EvaluationCriteria.objects.all()
    serializer_class = EvaluationCriteriaSerializer


class ProductionStageTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductionStageType.objects.all()
    serializer_class = ProductionStageTypeSerializer


class RiskThresholdViewSet(viewsets.ModelViewSet):
    queryset = RiskThreshold.objects.all()
    serializer_class = RiskThresholdSerializer


class DepartmentRoleViewSet(viewsets.ModelViewSet):
    queryset = DepartmentRole.objects.all()
    serializer_class = DepartmentRoleSerializer
