from twilio.rest import Client

def send_whatsapp_message(to_number, message):
    client = Client('ACCOUNT_SID', 'AUTH_TOKEN')
    client.messages.create(
        body=message,
        from_='whatsapp:+14155238886',
        to=f'whatsapp:{to_number}'
    )

