from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    path('', views.shipment_list, name='shipment_list'),
    path('create/', views.create_shipment, name='create_shipment'),
    path('update/<int:pk>/', views.update_shipment, name='update_shipment'),
    path('track/<str:tracking_number>/', views.track_shipment, name='track_shipment'),
]
