from django import forms
from .models import SupportTicket

class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['title', 'description', 'client', 'invoice', 'priority', 'status', 'assigned_to']
