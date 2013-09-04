from django.shortcuts import render

def index(request):
    return render(request, 'common/admin/dashboard.html')

def intro(request):
    return render(request, 'common/admin/intro.html')
