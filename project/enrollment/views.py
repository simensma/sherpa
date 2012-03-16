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
        request.session['registration'] = {'users': []}

    if user is not None:
        user = request.session['registration']['users'][int(user)]

    saved = False
    if(request.method == 'POST'):
        if not request.POST.has_key('skip'):
            if request.POST.has_key('user'):
                request.session['registration']['users'][int(request.POST['user'])] = parse_user_data(request)
            else:
                request.session['registration']['users'].append(parse_user_data(request))
            request.session['registration']['address'] = request.POST['address']
            request.session['registration']['zipcode'] = request.POST['zipcode']
            saved = True

        if(request.POST['next'] == "done"):
            return HttpResponseRedirect(reverse("enrollment.views.household"))

    # Update indices in case they have changed
    i = 0
    for reg in request.session['registration']['users']:
        reg['index'] = i
        i += 1

    context = {'users': request.session['registration']['users'], 'user': user, 'saved': saved,
        'address': request.session['registration'].get('address', ''),
        'zipcode': request.session['registration'].get('zipcode', '')}
    return render(request, 'enrollment/registration.html', context)

def remove(request, user):
    del request.session['registration']['users'][int(user)]
    if(len(request.session['registration']['users']) == 0):
        del request.session['registration']['address']
        del request.session['registration']['zipcode']
    return HttpResponseRedirect(reverse("enrollment.views.registration"))

def household(request):
    context = {'users': request.session['registration']['users'],
        'address': request.session['registration']['address'],
        'zipcode': request.session['registration']['zipcode']}
    if(len(request.session['registration']['users']) > 1):
        return render(request, 'enrollment/household.multiple.html', context)
    else:
        return render(request, 'enrollment/household.single.html', context)

def verification(request):
    # Todo: verify that 'registration' is set in session
    context = {'users': request.session['registration']['users'],
        'address': request.session['registration']['address'],
        'zipcode': request.session['registration']['zipcode']}
    return render(request, 'enrollment/verification.html', context)

def zipcode(request, code):
    location = Zipcode.objects.get(code=code).location
    return HttpResponse(str(location))

def parse_user_data(request):
    user = {}
    user['name'] = request.POST['name']
    user['dob'] = request.POST['dob']
    user['age'] = datetime.now().isocalendar()[0] - datetime.strptime(user['dob'], "%d.%m.%Y").isocalendar()[0]
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
