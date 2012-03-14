from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from user.models import Zipcode

from datetime import datetime, timedelta

def index(request):
    return HttpResponse()

def types(request):
    return render(request, 'enrollment/types.html')

def registration1(request):
    return render(request, 'enrollment/registration.1.html')

def registration2(request):
    # Todo: Verify values from form 1, redirect back if invalid
    if(request.method == 'POST'):
        registration = {}
        registration['name'] = request.POST['name']
        registration['dob'] = datetime.strptime(request.POST['dob'], "%d.%m.%Y")
        registration['address'] = request.POST['address']
        registration['zipcode'] = request.POST['zipcode']
        registration['location'] = Zipcode.objects.get(code=request.POST['zipcode']).location
        registration['phone'] = request.POST['phone']
        registration['email'] = request.POST['email']

        age = datetime.now().isocalendar()[0] - registration['dob'].isocalendar()[0]
        if(age > 26):
            registration['membership'] = 'Hovedmedlem'
        elif(age <= 26 and age > 19):
            registration['membership'] = 'Student/ungdom'
        elif(age <= 18 and age > 13):
            registration['membership'] = 'Skoleungdom'
        elif(age <= 13):
            registration['membership'] = 'Barnemedlem'

        request.session['registration'] = registration

    context = {'registration': request.session['registration']}
    return render(request, 'enrollment/registration.2.html', context)

def zipcode(request, code):
    location = Zipcode.objects.get(code=code).location
    return HttpResponse(str(location))
