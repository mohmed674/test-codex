# apps/qms/urls.py — Normalized (Sprint 2 / QMS CAPA-Audit-Complaints)

from django.urls import path
from . import views

app_name = "qms"

urlpatterns = [
    # Standardized entry
    path('', views.app_home, name='index'),
    path('list/', views.QMSHomeView.as_view(), name='list'),

    # AQL Plans
    path('aql/plans/', views.AQLPlanListView.as_view(), name='aql_plan_list'),
    path('aql/plans/create/', views.AQLPlanCreateView.as_view(), name='aql_plan_create'),
    path('aql/plans/<int:pk>/', views.AQLPlanDetailView.as_view(), name='aql_plan_detail'),
    path('aql/plans/<int:pk>/edit/', views.AQLPlanUpdateView.as_view(), name='aql_plan_update'),

    # AQL Lots & Results
    path('aql/lots/', views.InspectionLotListView.as_view(), name='aql_lot_list'),
    path('aql/lots/create/', views.InspectionLotCreateView.as_view(), name='aql_lot_create'),
    path('aql/lots/<int:pk>/', views.InspectionLotDetailView.as_view(), name='aql_lot_detail'),
    path('aql/lots/<int:pk>/edit/', views.InspectionLotUpdateView.as_view(), name='aql_lot_update'),
    path('aql/results/create/', views.InspectionResultCreateView.as_view(), name='aql_result_create'),
    path('aql/compute-sampling/', views.AQLComputeSamplingView.as_view(), name='aql_compute_sampling'),

    # SPC Processes & Charts
    path('spc/processes/', views.ControlProcessListView.as_view(), name='spc_process_list'),
    path('spc/processes/create/', views.ControlProcessCreateView.as_view(), name='spc_process_create'),
    path('spc/processes/<int:pk>/', views.ControlProcessDetailView.as_view(), name='spc_process_detail'),
    path('spc/processes/<int:pk>/edit/', views.ControlProcessUpdateView.as_view(), name='spc_process_update'),

    path('spc/charts/', views.ControlChartListView.as_view(), name='spc_chart_list'),
    path('spc/charts/create/', views.ControlChartCreateView.as_view(), name='spc_chart_create'),
    path('spc/charts/<int:pk>/', views.ControlChartDetailView.as_view(), name='spc_chart_detail'),
    path('spc/charts/<int:pk>/edit/', views.ControlChartUpdateView.as_view(), name='spc_chart_update'),

    path('spc/charts/<int:chart_id>/subgroups/', views.SubgroupListView.as_view(), name='spc_subgroup_list'),
    path('spc/charts/<int:chart_id>/subgroups/new/', views.SubgroupCreateView.as_view(), name='spc_subgroup_create'),
    path('spc/subgroups/<int:subgroup_id>/points/create/', views.DataPointCreateView.as_view(), name='spc_point_create'),

    # CAPA Records & Actions
    path('capa/records/', views.CAPARecordListView.as_view(), name='capa_record_list'),
    path('capa/records/create/', views.CAPARecordCreateView.as_view(), name='capa_record_create'),
    path('capa/records/<int:pk>/', views.CAPARecordDetailView.as_view(), name='capa_record_detail'),
    path('capa/records/<int:pk>/edit/', views.CAPARecordUpdateView.as_view(), name='capa_record_update'),

    path('capa/actions/create/', views.CAPAActionCreateView.as_view(), name='capa_action_create'),
    path('capa/actions/<int:pk>/edit/', views.CAPAActionUpdateView.as_view(), name='capa_action_update'),

    path('capa/change-status/', views.CAPAChangeStatusView.as_view(), name='capa_change_status'),
]
