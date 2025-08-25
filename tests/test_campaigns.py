import pytest
from django.urls import reverse
from django.utils import timezone
from apps.campaigns.models import Campaign
from apps.employees.models import Employee
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_create_campaign_view(client):
    # إنشاء مستخدم وموظف
    user = User.objects.create_user(username='tester', password='pass')
    employee = Employee.objects.create(user=user, full_name='Tester')
    client.force_login(user)

    data = {
        'name': 'اختبار حملة',
        'content': 'محتوى اختبار الحملة',
        'channel': 'email',
        'scheduled_date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
    }

    response = client.post(reverse('campaigns:create'), data)
    
    # تأكد أن إعادة التوجيه تمت بعد الإنشاء
    assert response.status_code == 302
    assert Campaign.objects.filter(name='اختبار حملة').exists()
