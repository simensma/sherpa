# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from user.models import Zipcode

from datetime import datetime, timedelta

def index(request):
    return HttpResponseRedirect(reverse("enrollment.views.registration"))

def types(request):
    return render(request, 'enrollment/types.html')

def conditions(request):
    return render(request, 'enrollment/conditions.html')

def registration(request, user):
    if not request.session.has_key('registration'):
        request.session['registration'] = []

    if user is not None:
        user = request.session['registration'][user]

    if(request.method == 'POST'):
        if request.POST.has_key('user'):
            request.session['registration'][int(request.POST['user'])] = parse_user_data(request)
        else:
            request.session['registration'].append(parse_user_data(request))

        if(request.POST['next'] == "done"):
            return HttpResponseRedirect(reverse("enrollment.views.verification"))

    # Update indices in case they have changed
    i = 0
    for user in request.session['registration']:
        user['index'] = i
        i += 1

    context = {'users': request.session['registration'], 'user': user}
    return render(request, 'enrollment/registration.html', context)

def remove(request, user):
    del request.session['registration'][int(user)]
    return HttpResponseRedirect(reverse("enrollment.views.registration"))

def verification(request):
    # Todo: verify that 'registration' is set in session
    context = {'users': request.session['registration']}
    return render(request, 'enrollment/verification.html', context)

def zipcode(request, code):
    location = Zipcode.objects.get(code=code).location
    return HttpResponse(str(location))

def parse_user_data(request):
    user = {}
    user['name'] = request.POST['name']
    user['dob'] = request.POST['dob']
    user['address'] = request.POST['address']
    user['zipcode'] = request.POST['zipcode']
    user['phone'] = request.POST['phone']
    user['email'] = request.POST['email']

    if(request.POST.get('key') == 'on'):
        user['key'] = True
    return user

def verify_user_data(user):
    dob = datetime.strptime(user['dob'], "%d.%m.%Y")
    location = Zipcode.objects.get(code=user['zipcode']).location

    age = datetime.now().isocalendar()[0] - dob.isocalendar()[0]
    if(age > 66):
        user['membership'] = 'Honnørmedlem'
        user['membershipreason'] = '(67 år eller mer)'
    elif(age <= 66 and age > 26):
        user['membership'] = 'Hovedmedlem'
        user['membershipreason'] = '(27 - 66 år)'
    elif(age <= 26 and age > 19):
        user['membership'] = 'Student/ungdom'
        user['membershipreason'] = '(20 - 26 år)'
    elif(age <= 18 and age > 13):
        user['membership'] = 'Skoleungdom'
        user['membershipreason'] = '(14 - 19 år)'
    elif(age <= 13):
        user['membership'] = 'Barnemedlem'
        user['membershipreason'] = '(13 år eller yngre)'
