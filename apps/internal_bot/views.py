from django.shortcuts import render
from .models import BotMessage
from .forms import BotForm
from django.contrib.auth.decorators import login_required

@login_required
def chat_with_bot(request):
    response = None
    if request.method == 'POST':
        form = BotForm(request.POST)
        if form.is_valid():
            question = form.cleaned_data['question']
            # رد افتراضي – يمكن ربطه لاحقًا بـ ChatGPT API
            answer = smart_bot_response(question)
            BotMessage.objects.create(user=request.user, question=question, answer=answer)
            response = answer
    else:
        form = BotForm()

    messages = BotMessage.objects.filter(user=request.user).order_by('-timestamp')[:10]
    return render(request, 'internal_bot/chat.html', {'form': form, 'response': response, 'messages': messages})

def smart_bot_response(question):
    # منطق الرد الذكي – يمكن استبداله بـ GPT لاحقًا
    if "فاتورة" in question:
        return "يمكنك الوصول إلى فواتيرك من قسم المبيعات أو بوابة العملاء."
    elif "رصيدي" in question:
        return "للاطلاع على رصيدك، توجه إلى قسم الحسابات > العملاء."
    else:
        return "جارٍ معالجة استفسارك، سيتم الرد قريبًا."


from django.shortcuts import render

def index(request):
    return render(request, 'internal_bot/index.html')


def app_home(request):
    return render(request, 'apps/internal_bot/home.html', {'app': 'internal_bot'})
