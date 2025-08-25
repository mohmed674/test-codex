from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    # ❌ السطر التالي يسبب كسر لأن الدالة غير موجودة
    # path('portfolios/', views.portfolio_list, name='portfolio_list'),
]
