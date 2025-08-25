from django import forms
from .models import SupportTicket, SupportResponse

class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['title', 'description', 'client', 'invoice', 'priority', 'assigned_to']

class SupportResponseForm(forms.ModelForm):
    class Meta:
        model = SupportResponse
        fields = ['message']
