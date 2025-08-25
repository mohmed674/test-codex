# apps/site/urls.py — Normalized (Sprint 1 / Site P1)

app_name = 'site'
from django.urls import path
from .views import home, about, contact

urlpatterns = [
    # Standardized index
    path('', home, name='index'),
    path('list/', home, name='list'),

    # Info pages
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),

    # Legacy aliases (for compatibility with old templates if any)
    path('legacy/home/', home, name='site_home'),
    path('legacy/about/', about, name='site_about'),
    path('legacy/contact/', contact, name='site_contact'),
]
