from django.urls import path
from . import views

app_name = "plm"

urlpatterns = [
    path("", views.home, name="home"),

    # 🟢 Products
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),

    # 🟢 Lifecycle
    path("stages/", views.lifecycle_stages, name="lifecycle_stages"),
    path("products/<int:pk>/lifecycle/", views.product_lifecycle, name="product_lifecycle"),

    # 🟢 Documents & Reviews
    path("documents/", views.documents_list, name="documents_list"),
    path("documents/<int:pk>/reviews/", views.document_reviews, name="document_reviews"),
]

from . import views
urlpatterns = (urlpatterns if 'urlpatterns' in globals() else []) + [
    path('', views.app_home, name='home'),
]
