# ERP_CORE/clients/tasks.py

from celery import shared_task
from .models import Client
from apps.accounting.models import Account

@shared_task
def auto_create_financial_accounts_for_clients():
    """
    مهمة ذكية لإنشاء حساب مالي لكل عميل ليس لديه حساب.
    """
    clients = Client.objects.filter(account_number__isnull=True)
    for client in clients:
        account = Account.objects.create(
            name=client.name,
            type='client',
            linked_client=client
        )
        client.account_number = account.number
        client.save()
