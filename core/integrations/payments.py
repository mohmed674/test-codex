import requests

def initiate_fawry_payment(amount, customer_name, phone, email):
    payload = {
        'merchantCode': 'YOUR_MERCHANT_CODE',
        'customerName': customer_name,
        'customerMobile': phone,
        'customerEmail': email,
        'amount': amount,
        'paymentExpiry': 24,
        'chargeItems': [{'itemId': '001', 'description': 'فاتورة', 'price': amount, 'quantity': 1}],
        'signature': 'GENERATED_SIGNATURE',
    }
    response = requests.post('https://www.atfawry.com/ECommerceWeb/Fawry/payments', json=payload)
    return response.json()
