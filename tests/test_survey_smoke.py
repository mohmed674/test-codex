import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
def test_survey_index_or_detail_accessible():
    client = Client()
    response = client.get("/survey/")  # غيّر للمسار الصحيح إن لزم
    assert response.status_code in (200, 302)
