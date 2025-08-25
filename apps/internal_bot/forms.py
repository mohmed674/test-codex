from django import forms

class BotForm(forms.Form):
    question = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label="ما هو سؤالك؟")
