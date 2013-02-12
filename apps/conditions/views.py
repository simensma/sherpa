from django.shortcuts import render


def index(request):
    return render(request, 'main/conditions/index.html')
