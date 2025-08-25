from django.core.mail import send_mail

def send_email(client, campaign):
    try:
        send_mail(
            subject=campaign.name,
            message=campaign.content,
            from_email='noreply@erp.local',
            recipient_list=[client.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def send_sms(client, campaign):
    try:
        # TODO: ربط مع مزود SMS حقيقي (مثل Twilio أو gateway محلي)
        print(f"[SMS] إلى {client.phone}: {campaign.content}")
        return True
    except Exception as e:
        print(f"[SMS ERROR] {e}")
        return False

def send_whatsapp(client, campaign):
    try:
        # TODO: ربط مع WhatsApp API أو مزود مثل Gupshup / Twilio
        print(f"[WhatsApp] إلى {client.phone}: {campaign.content}")
        return True
    except Exception as e:
        print(f"[WHATSAPP ERROR] {e}")
        return False
