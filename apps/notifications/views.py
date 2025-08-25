from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import datetime
import csv

from .models import Notification
from .serializers import NotificationSerializer
from .permissions import IsOwnerOrManager


# DRF ViewSet للـ API
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsOwnerOrManager]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Notification.objects.all().order_by('-created_at')
        return Notification.objects.filter(user=user).order_by('-created_at')

    # علامة قراءة على إشعار محدد
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = get_object_or_404(self.get_queryset(), pk=pk)
        notification.read = True
        notification.save()
        return Response({'status': 'marked as read'})


# الواجهات العادية للويب
@login_required
def notification_list(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        notifications = Notification.objects.all().order_by('-created_at')
    else:
        notifications = Notification.objects.filter(user=user).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})


@login_required
def mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.user != notification.user and not request.user.is_staff:
        return HttpResponse("غير مصرح", status=403)
    notification.read = True
    notification.save()
    return redirect('notifications:list')


# تصدير PDF
@login_required
def export_notifications_pdf(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        notifications = Notification.objects.all().order_by('-created_at')
    else:
        notifications = Notification.objects.filter(user=user).order_by('-created_at')

    html_string = render_to_string('notifications/pdf_list.html', {'notifications': notifications})
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"notifications_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# تصدير Excel (CSV)
@login_required
def export_notifications_excel(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        notifications = Notification.objects.all().order_by('-created_at')
    else:
        notifications = Notification.objects.filter(user=user).order_by('-created_at')

    response = HttpResponse(content_type='text/csv')
    filename = f"notifications_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'User', 'Message', 'Created At', 'Read'])
    for n in notifications:
        writer.writerow([n.id, n.user.username, n.message, n.created_at.strftime('%Y-%m-%d %H:%M'), n.read])

    return response


from django.shortcuts import render

def index(request):
    return render(request, 'notifications/index.html')


def app_home(request):
    return render(request, 'apps/notifications/home.html', {'app': 'notifications'})
