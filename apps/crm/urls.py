from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('leads/', views.lead_list, name='lead_list'),
    path('lead/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('lead/<int:pk>/interaction/', views.add_interaction, name='add_interaction'),
    path('lead/<int:pk>/opportunity/', views.add_opportunity, name='add_opportunity'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
