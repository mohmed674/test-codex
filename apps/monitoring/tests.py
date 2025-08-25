# ERP_CORE/monitoring/tests.py

from django.test import TestCase
from .models import Client, DistributionOrder, Shipment

class MonitoringModelsTestCase(TestCase):

    def setUp(self):
        self.client_obj = Client.objects.create(name="شركة التجربة", contact="01000000000")
        self.order = DistributionOrder.objects.create(
            client=self.client_obj,
            product_name="منتج تجريبي",
            quantity=50,
            status="Pending"
        )

    def test_client_creation(self):
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(self.client_obj.name, "شركة التجربة")

    def test_order_creation(self):
        self.assertEqual(DistributionOrder.objects.count(), 1)
        self.assertEqual(self.order.product_name, "منتج تجريبي")
        self.assertEqual(self.order.client, self.client_obj)

    def test_shipment_creation(self):
        shipment = Shipment.objects.create(
            tracking_number="TRK123456",
            order=self.order,
            status="In Transit"
        )
        self.assertEqual(Shipment.objects.count(), 1)
        self.assertEqual(shipment.order.product_name, "منتج تجريبي")
        self.assertEqual(shipment.tracking_number, "TRK123456")
