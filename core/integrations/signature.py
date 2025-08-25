import base64
import requests

def request_signature(pdf_url, client_email):
    payload = {
        "document": pdf_url,
        "recipient": client_email,
        "title": "توقيع عقد",
    }
    response = requests.post('https://api.signature-service.com/send', json=payload)
    return response.json()
