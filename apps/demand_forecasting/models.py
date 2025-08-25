from django.db import models
from apps.products.models import Product

class Forecast(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    forecast_month = models.DateField()
    predicted_quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.forecast_month}"
