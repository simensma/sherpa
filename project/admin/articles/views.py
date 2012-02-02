from django.shortcuts import render

def list(request):
    context = {}
    return render(request, 'admin/articles/list.html', context)

def new(request):
    context = {}
    return render(request, 'admin/articles/new.html', context)
