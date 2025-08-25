import pytest
from django.test import Client

@pytest.mark.django_db
def test_monitoring_dashboard_access():
    client = Client()
    response = client.get("/employee-monitoring/")  # تأكد من المسار
    assert response.status_code in (200, 302)
