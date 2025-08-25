from django.db import models

class VoiceCommand(models.Model):
    user = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    audio_file = models.FileField(upload_to='voice_commands/')
    transcript = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
