from django import forms
from .models import Zone, Location

class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = '__all__'

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = '__all__'
