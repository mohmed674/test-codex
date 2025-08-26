from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from .models import Survey, SurveyQuestion, SurveyResponse, Answer
from .forms import SurveyForm
try:
    from core.utils import render_to_pdf, export_to_excel  # type: ignore
except Exception:  # pragma: no cover
    def render_to_pdf(*args, **kwargs):  # نوع بديل بسيط للاختبارات
        return HttpResponse(b"", content_type="application/pdf")

    def export_to_excel(*args, **kwargs):
        return HttpResponse(b"", content_type="application/vnd.ms-excel")

# ✅ تعبئة الاستبيان
def take_survey(request, survey_id):
    survey = get_object_or_404(Survey, pk=survey_id)
    if request.method == 'POST':
        form = SurveyForm(request.POST, survey=survey)
        if form.is_valid():
            response = SurveyResponse.objects.create(survey=survey)
            for question in survey.surveyquestion_set.all():
                field_name = f"question_{question.id}"
                answer_value = form.cleaned_data.get(field_name)
                if question.question_type == 'text':
                    Answer.objects.create(response=response, question=question, answer_text=answer_value)
                elif question.question_type == 'multiple_choice':
                    choice = question.surveychoice_set.get(id=answer_value)
                    Answer.objects.create(response=response, question=question, selected_choice=choice)
            return render(request, 'survey/thanks.html')
    else:
        form = SurveyForm(survey=survey)
    return render(request, 'survey/take_survey.html', {'survey': survey, 'form': form})


# ✅ عرض نتائج استبيان محدد
def survey_results(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    responses = SurveyResponse.objects.filter(survey=survey).order_by('-submitted_at')
    questions = survey.surveyquestion_set.prefetch_related('surveychoice_set')
    answers = Answer.objects.filter(response__survey=survey).select_related('question', 'selected_choice')

    results_by_question = {}
    for question in questions:
        q_answers = answers.filter(question=question)
        results_by_question[question] = q_answers

    return render(request, 'survey/survey_results.html', {
        'survey': survey,
        'questions': questions,
        'results_by_question': results_by_question,
        'responses': responses,
    })


# ✅ تصدير PDF
def export_survey_pdf(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    answers = Answer.objects.filter(response__survey=survey).select_related('question', 'selected_choice')
    questions = survey.surveyquestion_set.all()

    results_by_question = {}
    for question in questions:
        results_by_question[question] = answers.filter(question=question)

    html = get_template("survey/survey_results_pdf.html").render({
        'survey': survey,
        'results_by_question': results_by_question
    })
    pdf_file = render_to_pdf(template_src=None, html_string=html)
    return HttpResponse(pdf_file, content_type="application/pdf")


# ✅ تصدير Excel
def export_survey_excel(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    answers = Answer.objects.filter(response__survey=survey).select_related('question', 'selected_choice')

    data = []
    for ans in answers:
        data.append({
            "السؤال": ans.question.question_text,
            "الإجابة النصية": ans.answer_text or "",
            "الاختيار": ans.selected_choice.choice_text if ans.selected_choice else "",
            "تاريخ التقديم": ans.response.submitted_at.strftime('%Y-%m-%d %H:%M'),
        })

    return export_to_excel(data, filename=f"survey_{survey.id}_results.xlsx")


# ✅ رسالة الشكر
def thanks(request):
    return render(request, 'survey/thanks.html')


from django.shortcuts import render

def index(request):
    return render(request, 'survey/index.html')


def app_home(request):
    return render(request, 'apps/survey/home.html', {'app': 'survey'})
