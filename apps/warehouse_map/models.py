from django.db import models

class Zone(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    label = models.CharField(max_length=50)
    capacity = models.IntegerField()
    current_occupancy = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.zone.code} - {self.label}"
