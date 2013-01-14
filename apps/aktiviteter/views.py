from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def index(request):
    context = {}
    return render(request, 'common/aktiviteter/index.html', context)
