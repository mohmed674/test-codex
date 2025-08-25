from django import forms
from .models import PatternDesign, PatternPiece, PatternExecution

class PatternDesignForm(forms.ModelForm):
    class Meta:
        model = PatternDesign
        fields = ['name', 'description', 'image', 'gerber_file', 'pattern_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class PatternPieceForm(forms.ModelForm):
    class Meta:
        model = PatternPiece
        fields = ['design', 'name', 'fabric_type', 'length_cm', 'width_cm', 'quantity']

class PatternExecutionForm(forms.ModelForm):
    class Meta:
        model = PatternExecution
        fields = ['production_order', 'design', 'notes', 'operator_name']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
