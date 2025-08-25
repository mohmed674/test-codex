from django.shortcuts import redirect, render
from .forms import VoiceCommandForm
from .models import VoiceCommand
from .speech_to_text import transcribe_audio
from django.contrib import messages

# ✅ عرض سجل الأوامر الصوتية
def voice_logs(request):
    # إصلاح الحقل غير الموجود: استخدام timestamp بدل created_at
    logs = VoiceCommand.objects.all().order_by('-timestamp')
    return render(request, 'voice_commands/logs.html', {'logs': logs})

# ✅ رفع أمر صوتي وتحويله إلى نص
def upload_voice(request):
    if request.method == 'POST':
        form = VoiceCommandForm(request.POST, request.FILES)
        if form.is_valid():
            command = form.save(commit=False)
            audio = request.FILES['audio_file']
            try:
                transcript = transcribe_audio(audio)
                command.transcript = transcript
                # إسناد المستخدم الحالي إن كان الحقل موجودًا بالموديل
                if hasattr(command, 'user_id') and request.user.is_authenticated:
                    command.user = request.user
                command.save()
                messages.success(request, f'✅ تم رفع الأمر الصوتي بنجاح. النص: {transcript[:100]}...')
                return redirect('voice_commands:voice_logs')
            except Exception as e:
                messages.error(request, f'❌ فشل تحويل الصوت لنص: {str(e)}')
        else:
            messages.warning(request, '⚠️ يرجى تصحيح الأخطاء في النموذج.')
    else:
        form = VoiceCommandForm()
    return render(request, 'voice_commands/upload.html', {'form': form})


from django.shortcuts import render

def index(request):
    return render(request, 'voice_commands/index.html')


def app_home(request):
    return render(request, 'apps/voice_commands/home.html', {'app': 'voice_commands'})
