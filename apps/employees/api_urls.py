# ERP_CORE/employees/api_urls.py

from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'employees', api_views.EmployeeViewSet)
router.register(r'attendance-records', api_views.AttendanceRecordViewSet)
router.register(r'monthly-incentives', api_views.MonthlyIncentiveViewSet)

urlpatterns = router.urls
