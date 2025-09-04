# ERP_CORE/whatsapp_bot/api_views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .ai_reply_engine import generate_auto_reply
from .models import WhatsAppOrder


@api_view(["POST"])
def receive_whatsapp_message(request):
    sender = request.data.get("sender")
    message = request.data.get("message")
    if not sender or not message:
        return Response({"status": "invalid"}, status=400)

    auto_reply = generate_auto_reply(message)

    order = WhatsAppOrder.objects.create(
        customer_phone=sender,
        message=message,
        reply=auto_reply,
        status="Auto-Reply Sent",
    )

    return Response({"status": "received", "reply": auto_reply})
