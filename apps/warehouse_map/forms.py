from django import forms

from .models import Location, Zone


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = "__all__"


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = "__all__"
