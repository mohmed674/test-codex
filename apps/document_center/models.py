from django.db import models
from django.contrib.auth.models import User

DOCUMENT_TYPES = [
    ('contract', 'عقد'),
    ('invoice', 'فاتورة'),
    ('report', 'تقرير'),
    ('other', 'أخرى'),
]

class Document(models.Model):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    department = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title
