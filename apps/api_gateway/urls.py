from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from . import views

app_name = 'api_gateway'

urlpatterns = [
    path('sales/', never_cache(login_required(views.sales_data)), name='sales_data'),
    path('clients/<int:client_id>/balance/', never_cache(login_required(views.client_balance)), name='client_balance'),
    path('products/stock/', never_cache(login_required(views.product_stock)), name='product_stock'),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
