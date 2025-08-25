import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_api_session(client, test_user):
    client.force_login(test_user)
    url = reverse('mobile:api_session')
    response = client.get(url)
    assert response.status_code == 200
    assert 'user_id' in response.json()
    assert response.json()['username'] == test_user.username
