from django.shortcuts import render, redirect
from .models import Article
from .forms import ArticleForm
from django.contrib.auth.decorators import login_required

@login_required
def article_list(request):
    articles = Article.objects.filter(is_active=True)
    return render(request, 'knowledge_center/article_list.html', {'articles': articles})

@login_required
def article_create(request):
    form = ArticleForm(request.POST or None)
    if form.is_valid():
        article = form.save(commit=False)
        article.created_by = request.user
        article.save()
        return redirect('knowledge_center:article_list')
    return render(request, 'knowledge_center/article_form.html', {'form': form})


from django.shortcuts import render

def index(request):
    return render(request, 'knowledge_center/index.html')


def app_home(request):
    return render(request, 'apps/knowledge_center/home.html', {'app': 'knowledge_center'})
