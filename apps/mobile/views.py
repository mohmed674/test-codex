from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now

# ============================
# واجهات العرض التقليدية
# ============================
@login_required
def mobile_dashboard(request):
    return render(request, 'mobile/dashboard.html')

def index(request):
    return render(request, 'mobile/index.html')

def app_home(request):
    return render(request, 'apps/mobile/home.html', {'app': 'mobile'})

# ============================
# REST APIs
# ============================

@login_required
def api_session(request):
    return JsonResponse({
        'user_id': request.user.id,
        'username': request.user.username,
        'full_name': request.user.get_full_name(),
        'employee_id': getattr(request.user, 'employee_id', None),
        'timestamp': now()
    })

@login_required
def api_menu(request):
    # TODO: استبداله ببيانات ديناميكية بناء على صلاحيات المستخدم
    return JsonResponse({
        'menu': [
            {'label': 'الرئيسية', 'url': '/mobile/'},
            {'label': 'الإشعارات', 'url': '/mobile/notifications'},
            {'label': 'المزامنة', 'url': '/mobile/sync'},
        ]
    })

@csrf_exempt
def api_offline_sync(request):
    if request.method == 'POST':
        # placeholder: استقبال بيانات وتأكيد الاستلام
        return JsonResponse({'status': '✅ synced'})
    return JsonResponse({'error': '❌ method not allowed'}, status=405)

@login_required
def api_notifications(request):
    # placeholder: قائمة إشعارات للمستخدم
    return JsonResponse({
        'notifications': [
            {'id': 1, 'title': 'تم تحديث المخزون', 'timestamp': str(now())},
            {'id': 2, 'title': 'مهمة جديدة تم تعيينها إليك', 'timestamp': str(now())},
        ]
    })
