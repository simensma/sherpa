# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from user.models import Zipcode

from datetime import datetime, timedelta

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

    updateIndices(request)
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
    updateIndices(request)
    context = {'users': request.session['registration']['users'],
        'existing': request.session['registration']['existing']}
    return render(request, 'enrollment/household.html', context)

def verification(request):
    # Todo: verify that 'registration' is set in session
    request.session['registration']['existing'] = request.POST.get('existing', '')
    request.session['registration']['location'] = Zipcode.objects.get(code=request.session['registration']['zipcode']).location
    keycount = 0
    over_13 = 0
    main = None
    for user in request.session['registration']['users']:
        if(main == None or (user['age'] < main['age'] and user['age'] > 18)):
            # The cheapest option will be to set the youngest member, 19 or older, as main member
            main = user
        if(user['age'] > 13):
            over_13 += 1
        if user.has_key('key'):
            keycount += 1
    keyprice = keycount * KEY_PRICE
    multiple_main = over_13 > 1
    updateIndices(request)
    context = {'users': request.session['registration']['users'],
        'address': request.session['registration']['address'],
        'zipcode': request.session['registration']['zipcode'],
        'location': request.session['registration']['location'],
        'existing': request.session['registration']['existing'],
        'keycount': keycount, 'keyprice': keyprice, 'multiple_main': multiple_main,
        'main': main}
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

def updateIndices(request):
    i = 0
    for reg in request.session['registration']['users']:
        reg['index'] = i
        i += 1
