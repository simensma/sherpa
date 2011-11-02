from django.shortcuts import render

def index(request):
    return render(request, 'training/training.html')

def hikeleader(request):
    return render(request, 'training/hikeleader.html')
