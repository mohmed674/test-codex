# ERP_CORE/suppliers/api_views.py

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Supplier
from .serializers import SupplierSerializer
from apps.accounting.models import SupplierInvoice
from .permissions import IsManagerOrReadOnly

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('-id')
    serializer_class = SupplierSerializer
    permission_classes = [IsManagerOrReadOnly]

    @action(detail=True, methods=['get'], url_path='invoices')
    def supplier_invoices(self, request, pk=None):
        supplier = self.get_object()
        invoices = SupplierInvoice.objects.filter(supplier=supplier)
        data = [{
            "number": inv.number,
            "total": inv.total_amount,
            "status": inv.get_status_display(),
            "issued": inv.date_issued,
            "due": inv.due_date
        } for inv in invoices]
        return Response(data)
