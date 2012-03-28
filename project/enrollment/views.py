# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from user.models import Zipcode

from datetime import datetime, timedelta
import re

KEY_PRICE = 100

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
    errors = False
    if(request.method == 'POST'):
        new_user = {}
        new_user['name'] = request.POST['name']
        new_user['phone'] = request.POST['phone']
        new_user['email'] = request.POST['email']
        request.session['registration']['address'] = request.POST['address']
        request.session['registration']['zipcode'] = request.POST['zipcode']
        if(request.POST.get('key') == 'on'):
            new_user['key'] = True

        try:
            new_user['dob'] = datetime.strptime(request.POST['dob'], "%d.%m.%Y")
            new_user['age'] = datetime.now().isocalendar()[0] - new_user['dob'].isocalendar()[0]
        except ValueError:
            new_user['dob'] = None
            new_user['age'] = None

        if not validate_user(request.POST) or not validate_location(request.POST['address'], request.POST['zipcode']):
            errors = True
            if request.POST.has_key('user'):
                index = int(request.POST['user'])
                user = new_user
                user['index'] = index
            else:
                user = new_user
        else:
            if request.POST.has_key('user'):
                request.session['registration']['users'][int(request.POST['user'])] = new_user
            else:
                request.session['registration']['users'].append(new_user)
            saved = True

    updateIndices(request)

    if not errors and request.POST.has_key('forward'):
        return HttpResponseRedirect(reverse("enrollment.views.household"))

    context = {'users': request.session['registration']['users'], 'user': user,
        'saved': saved, 'errors': errors,
        'address': request.session['registration'].get('address', ''),
        'zipcode': request.session['registration'].get('zipcode', ''),
        'conditions': request.session['registration'].get('conditions', '')}
    return render(request, 'enrollment/registration.html', context)

def remove(request, user):
    del request.session['registration']['users'][int(user)]
    if(len(request.session['registration']['users']) == 0):
        del request.session['registration']['address']
        del request.session['registration']['zipcode']
    return HttpResponseRedirect(reverse("enrollment.views.registration"))

def household(request):
    if not request.session.has_key('registration'):
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    request.session['registration']['conditions'] = True
    if len(request.session['registration']['users']) == 0:
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    updateIndices(request)
    context = {'users': request.session['registration']['users'],
        'existing': request.session['registration'].get('existing', '')}
    return render(request, 'enrollment/household.html', context)

def verification(request):
    if not request.session.has_key('registration'):
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    if len(request.session['registration']['users']) == 0:
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    # Todo: verify that 'registration' is set in session
    request.session['registration']['existing'] = request.POST.get('existing', '')
    request.session['registration']['location'] = Zipcode.objects.get(code=request.session['registration']['zipcode']).location
    keycount = 0
    over_18 = 0
    main = None
    for user in request.session['registration']['users']:
        if(main == None or (user['age'] < main['age'] and user['age'] > 18)):
            # The cheapest option will be to set the youngest member, 19 or older, as main member
            main = user
        if(user['age'] > 18):
            over_18 += 1
        if user.has_key('key'):
            keycount += 1
    keyprice = keycount * KEY_PRICE
    multiple_main = over_18 > 1
    updateIndices(request)
    context = {'users': request.session['registration']['users'],
        'address': request.session['registration']['address'],
        'zipcode': request.session['registration']['zipcode'],
        'location': request.session['registration']['location'],
        'existing': request.session['registration']['existing'],
        'keycount': keycount, 'keyprice': keyprice, 'multiple_main': multiple_main,
        'main': main}
    return render(request, 'enrollment/verification.html', context)

# TODO: Remember to check that len(request.session['registration']['users']) > 0 when submitting step 3

def zipcode(request, code):
    location = Zipcode.objects.get(code=code).location
    return HttpResponse(str(location))

def updateIndices(request):
    i = 0
    for user in request.session['registration']['users']:
        user['index'] = i
        i += 1

def validate_user(user):
    # Name or address is empty
    if user['name'] == '':
        return False

    # Phone no. is less than 8 chars (allow >8, in case it's formatted with whitespace)
    if len(user['phone']) < 8:
        return False

    # Email is non-empty (empty is allowed) and doesn't match an email
    if(user['email'] != '' and len(re.findall('.+@.+\..+', user['email'])) == 0):
        return False

    # Date of birth is not valid format (%d.%m.%Y)
    # Will be unicode when posted, but datetime when saved
    if isinstance(user['dob'], unicode):
        try:
            datetime.strptime(user['dob'], "%d.%m.%Y")
        except ValueError:
            return False
    elif not isinstance(user['dob'], datetime):
        return False

    # All tests passed!
    return True

def validate_location(address, zipcode):
    # Address is empty
    if address == '':
        return False

    # Zipcode does not exist
    try:
        Zipcode.objects.get(code=zipcode)
    except Zipcode.DoesNotExist:
        return False

    # All tests passed!
    return True
