# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from user.models import Zipcode

from datetime import datetime, timedelta

def index(request):
    return HttpResponse()

def types(request):
    return render(request, 'enrollment/types.html')

def conditions(request):
    return render(request, 'enrollment/conditions.html')

def registration(request):
    if not request.session.has_key('registration'):
        request.session['registration'] = []

    prev = None
    current = None
    next = None

    if(request.method == 'POST'):
        # Todo: Verify values, redirect back if invalid
        if request.POST.has_key('user'):
            request.session['registration'][int(request.POST['user'])] = parse_user_data(request)
        else:
            request.session['registration'].append(parse_user_data(request))

        # Logic for traversing registrations
        if(request.POST['next'] == "done"):
            context = {'registration': request.session['registration']}
            return HttpResponseRedirect(reverse("enrollment.views.verification"), context)
        elif(request.POST['next'] == "new"):
            if(len(request.session['registration']) > 0):
                prev = {'index': len(request.session['registration']) - 1, 'name': request.session['registration'][len(request.session['registration']) - 1]['name']}
        else:
            current = {'index': int(request.POST['next'])}
            if(current['index'] != 0):
                prev = {'index': current['index'] - 1, 'name': request.session['registration'][current['index'] - 1]['name']}
            if(current['index'] < len(request.session['registration']) - 1):
                next = {'index': current['index'] + 1, 'name': request.session['registration'][current['index'] + 1]['name']}
            current['user'] = request.session['registration'][current['index']]
    else:
        if len(request.session['registration']) > 0:
            current = {'index': 0, 'user': request.session['registration'][0]}
            if len(request.session['registration']) > 1:
                next = {'index': 1, 'name': request.session['registration'][1]['name']}
    context = {'prev': prev, 'current': current, 'next': next}
    return render(request, 'enrollment/registration.html', context)

def verification(request):
    # Todo: verify that 'registration' is set in session
    context = {'registration': request.session['registration']}
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

    if(request.POST.get('household') == 'on'):
        user['household'] = True
        user['householdmember'] = request.POST['householdmember']

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
