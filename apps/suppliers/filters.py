# suppliers/filters.py

import django_filters
from apps.accounting.models import Supplier

class SupplierFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label="الاسم")
    governorate = django_filters.CharFilter(lookup_expr='icontains', label="المحافظة")
    phone = django_filters.CharFilter(lookup_expr='icontains', label="رقم الهاتف")

    class Meta:
        model = Supplier
        fields = ['name', 'governorate', 'phone']
