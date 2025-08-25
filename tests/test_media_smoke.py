import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
def test_media_homepage_accessible():
    client = Client()
    response = client.get("/media/")  # أو غيّرها لمسار صحيح لو اختلف
    assert response.status_code in (200, 302)
