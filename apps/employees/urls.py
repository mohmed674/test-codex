from django.urls import path
from .views import (
    EmployeeListView, EmployeeCreateView, EmployeeUpdateView,
    employee_profile
)

# تفعيل namespace لاستخدام employees:... في القوالب والـviews
app_name = 'employees'

urlpatterns = [
    path('', EmployeeListView.as_view(), name='list'),
    path('add/', EmployeeCreateView.as_view(), name='employee_add'),
    path('<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee_edit'),
    path('profile/<int:pk>/', employee_profile, name='employee_profile'),
]
