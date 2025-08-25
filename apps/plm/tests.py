from django.test import TestCase
from django.urls import reverse
from .models import ProductTemplate


class ProductTemplateTests(TestCase):
    def setUp(self):
        self.product = ProductTemplate.objects.create(
            name="Test Product",
            code="TP001",
            category="Test Category",
            uom="pcs",
        )

    def test_product_str(self):
        self.assertEqual(str(self.product), "TP001 - Test Product")

    def test_product_list_view(self):
        url = reverse("plm:product_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product")

    def test_product_detail_view(self):
        url = reverse("plm:product_detail", args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TP001")
