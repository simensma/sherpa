from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def list(request):
    context = {}
    return render(request, 'admin/articles/list.html', context)

def new(request):
    return HttpResponseRedirect(reverse('admin.articles.views.edit'))

def edit(request):
    context = {}
    return render(request, 'admin/articles/edit.html', context)
