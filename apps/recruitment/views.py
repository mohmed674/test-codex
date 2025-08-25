from django.shortcuts import render, redirect, get_object_or_404
from .models import JobPosition, Application
from .forms import ApplicationForm

def job_list(request):
    jobs = JobPosition.objects.filter(is_active=True)
    return render(request, 'recruitment/job_list.html', {'jobs': jobs})

def apply_job(request, job_id):
    job = get_object_or_404(JobPosition, id=job_id)
    form = ApplicationForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        application = form.save(commit=False)
        application.position = job
        application.save()
        return redirect('recruitment:job_list')
    return render(request, 'recruitment/apply_job.html', {'form': form, 'job': job})


from django.shortcuts import render

def index(request):
    return render(request, 'recruitment/index.html')


def app_home(request):
    return render(request, 'apps/recruitment/home.html', {'app': 'recruitment'})
