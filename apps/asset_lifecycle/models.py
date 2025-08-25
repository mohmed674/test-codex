from django.db import models

ASSET_STATUS = [
    ('active', 'نشط'),
    ('maintenance', 'صيانة'),
    ('disposed', 'تم التخلص منه'),
]

class Asset(models.Model):
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)
    purchase_date = models.DateField()
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=ASSET_STATUS, default='active')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"
