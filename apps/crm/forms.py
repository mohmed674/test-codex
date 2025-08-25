from django import forms
from .models import Lead, Interaction, Opportunity

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = '__all__'

class InteractionForm(forms.ModelForm):
    class Meta:
        model = Interaction
        fields = ['note']

class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = '__all__'
