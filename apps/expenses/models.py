from django.db import models

EXPENSE_CATEGORY = [
    ('operational', 'تشغيلية'),
    ('marketing', 'تسويق'),
    ('salary', 'رواتب'),
    ('maintenance', 'صيانة'),
    ('other', 'أخرى'),
]

class Expense(models.Model):
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=20, choices=EXPENSE_CATEGORY)
    date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title
