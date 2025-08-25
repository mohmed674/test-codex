from django import forms
from .models import VoiceCommand


class VoiceCommandForm(forms.ModelForm):
    class Meta:
        model = VoiceCommand
        fields = ['user', 'role', 'audio_file']
        labels = {
            'user': 'المستخدم',
            'role': 'الدور',
            'audio_file': 'ملف الصوت',
        }
        widgets = {
            'user': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المستخدم'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'audio_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
