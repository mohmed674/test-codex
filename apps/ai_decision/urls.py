# apps/ai_decision/urls.py — Routing normalized (Sprint 1 / Routing P1)

from django.urls import path
from .views import (
    ai_dashboard,
    ai_reports_dashboard,
    ai_sales_analysis_report,
    analyze_decision,
    decision_report,
    ai_report_pdf,
    ai_report_excel,
    ai_report_csv,
    decision_history_view,
    copilot_view,
    copilot_query,
)
from .views_future import (
    ai_learning_dashboard,
    ai_predictive_analysis,
    ai_decision_assistant_api,
    ai_visual_dashboard,
)
from .views_ocr import ocr_upload_view

app_name = 'ai_decision'

urlpatterns = [
    # Standardized entry
    path('', copilot_view, name='index'),
    path('list/', ai_dashboard, name='list'),
    path('create/', analyze_decision, name='create'),   # mapping analyze as "create decision"
    path('detail/<int:pk>/', decision_report, name='detail'),  # can expand with pk later
    path('update/<int:pk>/', analyze_decision, name='update'), # placeholder for consistency
    path('delete/<int:pk>/', decision_report, name='delete'),  # placeholder for consistency

    # Dashboards
    path('dashboard/', ai_dashboard, name='dashboard'),
    path('learning/dashboard/', ai_learning_dashboard, name='learning_dashboard'),
    path('reports/', ai_reports_dashboard, name='reports'),
    path('reports/dashboard/', ai_reports_dashboard, name='reports_dashboard'),
    path('sales-analysis/', ai_sales_analysis_report, name='sales_analysis'),

    # Decision & history
    path('analyze/', analyze_decision, name='analyze'),
    path('report/', decision_report, name='report'),
    path('history/', decision_history_view, name='history'),

    # Export
    path('report/pdf/', ai_report_pdf, name='export_pdf'),
    path('report/excel/', ai_report_excel, name='export_excel'),
    path('report/csv/', ai_report_csv, name='export_csv'),

    # Copilot
    path('copilot/', copilot_view, name='copilot'),
    path('query/', copilot_query, name='query'),

    # OCR
    path('ocr/upload/', ocr_upload_view, name='ocr_upload'),

    # Future / predictive AI
    path('predictive/', ai_predictive_analysis, name='predictive'),
    path('assistant-api/', ai_decision_assistant_api, name='assistant_api'),
    path('visual-dashboard/', ai_visual_dashboard, name='visual_dashboard'),
]
