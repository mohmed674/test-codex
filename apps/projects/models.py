from django.db import models
from apps.employees.models import Employee

class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'قيد التخطيط'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('paused', 'معلق'),
    ]

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='managed_projects')

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'قائمة المهام'),
        ('doing', 'قيد التنفيذ'),
        ('done', 'منجزة'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')

    def __str__(self):
        return f"{self.project.name} - {self.title}"
