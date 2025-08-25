import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
def test_employee_list_view_responds():
    client = Client()
    url = reverse("employees:list")  # غيّرها حسب اسم الـ URL فعليًا إن لزم
    response = client.get(url)
    assert response.status_code in (200, 302)
