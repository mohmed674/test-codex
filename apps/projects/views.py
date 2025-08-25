from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Task
from .forms import ProjectForm, TaskForm

def project_list(request):
    projects = Project.objects.all().order_by('-start_date')
    return render(request, 'projects/project_list.html', {'projects': projects})

def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('projects:project_list')
    else:
        form = ProjectForm()
    return render(request, 'projects/project_form.html', {'form': form})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all()
    task_form = TaskForm()
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'task_form': task_form
    })

def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
    return redirect('projects:project_detail', pk=task.project.id)



from django.shortcuts import render

def index(request):
    return render(request, 'projects/index.html')


def app_home(request):
    return render(request, 'apps/projects/home.html', {'app': 'projects'})
