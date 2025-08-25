from django.db import models

APPLICATION_STATUS = [
    ('pending', 'قيد المراجعة'),
    ('accepted', 'مقبول'),
    ('rejected', 'مرفوض'),
]

class JobPosition(models.Model):
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=100)
    description = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    position = models.ForeignKey(JobPosition, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    cv = models.FileField(upload_to='cv/')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.position.title}"
