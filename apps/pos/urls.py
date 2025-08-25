from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('open-session/', views.open_session, name='open_session'),
    path('close-session/<int:session_id>/', views.close_session, name='close_session'),
    path('new-order/<int:session_id>/', views.new_order, name='new_order'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
