from django import forms
from .models import Campaign

class CampaignForm(forms.ModelForm):
    scheduled_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="تاريخ الإرسال المجدول"
    )

    class Meta:
        model = Campaign
        fields = ['name', 'content', 'channel', 'scheduled_date']
        labels = {
            'name': 'اسم الحملة',
            'content': 'محتوى الرسالة',
            'channel': 'القناة',
        }
