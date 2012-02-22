from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from articles.models import Article
from page.models import Version

def list(request):
    versions = Version.objects.filter(variant__article__isnull=False, variant__segment__isnull=True, active=True)
    context = {'versions': versions}
    return render(request, 'admin/articles/list.html', context)

def new(request):
    article = Article(title=request.POST['title'], published=False, pub_date=None,
      publisher=request.user.get_profile())
    article.save()
    return HttpResponseRedirect(reverse('admin.articles.views.edit', args=[article.id]))

def edit(request, article):
    article = Article.objects.get(id=article)
    context = {'article': article}
    return render(request, 'admin/articles/edit.html', context)
