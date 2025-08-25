from django import forms
from .models import Survey, SurveyResponse, Answer, SurveyQuestion, SurveyChoice


class SurveyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey')
        super().__init__(*args, **kwargs)
        for question in survey.surveyquestion_set.all():
            field_name = f"question_{question.id}"
            if question.question_type == 'text':
                self.fields[field_name] = forms.CharField(
                    label=question.question_text,
                    widget=forms.Textarea(attrs={'rows': 3}),
                    required=False
                )
            elif question.question_type == 'multiple_choice':
                choices = [(choice.id, choice.choice_text) for choice in question.surveychoice_set.all()]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.question_text,
                    widget=forms.RadioSelect,
                    choices=choices,
                    required=False
                )
            elif question.question_type == 'rating':
                self.fields[field_name] = forms.IntegerField(
                    label=question.question_text,
                    min_value=1,
                    max_value=5,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'من 1 إلى 5'}),
                    required=False
                )
