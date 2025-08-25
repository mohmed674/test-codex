import pytest
from django.test import Client
from django.contrib.auth import get_user_model

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def test_user(db):
    User = get_user_model()
    return User.objects.create_user(username='testuser', password='testpass')
