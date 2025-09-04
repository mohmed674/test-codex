# apps/communication/views.py
from __future__ import annotations

from typing import Iterable

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MessageForm
from .models import ChatThread


def _thread_messages(thread: ChatThread) -> Iterable:
    """
    Return all messages for a thread regardless of related_name:
    tries `thread.messages.all()`, then `thread.message_set.all()`,
    finally queries a concrete Message model if present.
    """
    for rel_name in ("messages", "message_set"):
        rel = getattr(thread, rel_name, None)
        if rel is not None and hasattr(rel, "all"):
            return rel.all()

    Message = apps.get_model("communication", "Message")
    if Message is not None:
        try:
            # Discover FK name pointing to ChatThread
            for f in Message._meta.get_fields():  # type: ignore[attr-defined]
                if getattr(f, "is_relation", False) and getattr(
                    f, "many_to_one", False
                ):
                    if getattr(f, "related_model", None) is ChatThread:
                        return Message.objects.filter(**{f.name: thread}).all()
        except Exception:
            return Message.objects.none()
    return []


@login_required
def thread_list(request):
    threads = ChatThread.objects.filter(participants=request.user)
    return render(request, "communication/thread_list.html", {"threads": threads})


@login_required
def thread_chat(request, thread_id: int):
    thread = get_object_or_404(ChatThread, id=thread_id, participants=request.user)
    messages_qs = _thread_messages(thread)
    form = MessageForm(request.POST or None)
    if form.is_valid():
        msg = form.save(commit=False)
        msg.thread = thread  # assumes Message.thread FK exists; typical schema
        msg.sender = request.user
        msg.save()
        return redirect("communication:thread_chat", thread_id=thread.pk)
    return render(
        request,
        "communication/thread_chat.html",
        {"thread": thread, "messages": messages_qs, "form": form},
    )


def index(request):
    return render(request, "communication/index.html")


def app_home(request):
    return render(request, "apps/communication/home.html", {"app": "communication"})
