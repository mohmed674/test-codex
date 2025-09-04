# ERP_CORE/clients/tasks.py
from __future__ import annotations

from celery import shared_task
from django.db import transaction

from apps.accounting.models import Account

from .models import Client


@shared_task
def auto_create_financial_accounts_for_clients() -> None:
    """
    🟢 مهمة ذكية:
    إنشاء حساب مالي لكل عميل جديد لا يملك حساب في شجرة الحسابات.
    يفترض وجود حقل ForeignKey في Account اسمه linked_client لربط الحساب بالعميل.
    """
    clients = Client.objects.filter(partner__accounting_code__isnull=True)

    for client in clients:
        with transaction.atomic():
            account = Account.objects.create(
                name=str(client.partner.name),
                type="client",
                linked_client=client,
            )
            # استخدم code إن وُجد، وإلا pk (متوافق مع Pylance عبر getattr)
            account_identifier = getattr(account, "code", None)
            if not account_identifier:
                account_identifier = str(getattr(account, "pk", ""))

            client.partner.accounting_code = account_identifier
            client.partner.save(update_fields=["accounting_code"])
