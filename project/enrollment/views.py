from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from user.models import Zipcode

def index(request):
    return HttpResponse()

def registration1(request):
    return render(request, 'enrollment/registration.1.html')

def registration2(request):
    return render(request, 'enrollment/registration.2.html')

def zipcode(request, code):
    location = Zipcode.objects.get(code=code).location
    return HttpResponse(str(location))
