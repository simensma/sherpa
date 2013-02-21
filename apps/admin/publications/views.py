from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'common/admin/publications/index.html', context)
