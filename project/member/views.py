from django.shortcuts import render

def index(request):
    return render(request, 'member/member.html')

def register(request):
    return render(request, 'member/register.html')
