from django.shortcuts import render, redirect
from .models import Document
from .forms import DocumentForm
from django.contrib.auth.decorators import login_required

@login_required
def document_list(request):
    documents = Document.objects.all()
    query = request.GET.get('q')
    if query:
        documents = documents.filter(title__icontains=query)
    return render(request, 'document_center/document_list.html', {'documents': documents})

@login_required
def document_upload(request):
    form = DocumentForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        doc = form.save(commit=False)
        doc.uploaded_by = request.user
        doc.save()
        return redirect('document_center:document_list')
    return render(request, 'document_center/document_form.html', {'form': form})


from django.shortcuts import render

def index(request):
    return render(request, 'document_center/index.html')


def app_home(request):
    return render(request, 'apps/document_center/home.html', {'app': 'document_center'})
