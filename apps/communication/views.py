from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatThread, Message
from .forms import MessageForm
from django.contrib.auth.decorators import login_required

@login_required
def thread_list(request):
    threads = ChatThread.objects.filter(participants=request.user)
    return render(request, 'communication/thread_list.html', {'threads': threads})

@login_required
def thread_chat(request, thread_id):
    thread = get_object_or_404(ChatThread, id=thread_id, participants=request.user)
    messages = thread.message_set.all()
    form = MessageForm(request.POST or None)
    if form.is_valid():
        msg = form.save(commit=False)
        msg.thread = thread
        msg.sender = request.user
        msg.save()
        return redirect('communication:thread_chat', thread_id=thread.id)
    return render(request, 'communication/thread_chat.html', {'thread': thread, 'messages': messages, 'form': form})


from django.shortcuts import render

def index(request):
    return render(request, 'communication/index.html')


def app_home(request):
    return render(request, 'apps/communication/home.html', {'app': 'communication'})
