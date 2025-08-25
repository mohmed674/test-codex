from django import forms
from .models import DecisionAnalysis

class DecisionAnalysisForm(forms.ModelForm):
    class Meta:
        model = DecisionAnalysis
        fields = '__all__'


# ✅ نموذج رفع صورة أو ملف PDF لتحليل OCR
class OCRUploadForm(forms.Form):
    document = forms.FileField(
        label="ارفع صورة أو ملف PDF للفاتورة",
        widget=forms.ClearableFileInput(attrs={"accept": ".jpg,.jpeg,.png,.pdf"})
    )
