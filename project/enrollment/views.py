# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import Context, loader

from user.models import Zipcode

from datetime import datetime
import requests
import re
from lxml import etree

# From the start of this month, memberships are for the remaining year AND next year
# (1 = January, 12 = December)
MONTH_THRESHOLD = 10

KEY_PRICE = 100
contact_missing_key = 'mangler-kontaktinfo' # GET parameter used for error handling

REGISTER_URL = "https://epayment.bbs.no/Netaxept/Register.aspx"
TERMINAL_URL = "https://epayment.bbs.no/Terminal/default.aspx"
PROCESS_URL = "https://epayment.bbs.no/Netaxept/Process.aspx"

# Temporary hardcoded prices
PRICE_MAIN = 550
PRICE_HOUSEHOLD = 250
PRICE_SENIOR = 425
PRICE_STUDENT = 295
PRICE_SCHOOL = 175
PRICE_CHILD = 110

# Hardcoded ages
AGE_SENIOR = 68
AGE_MAIN = 27
AGE_STUDENT = 19
AGE_SCHOOL = 13

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
        # If the name is all lowercase or uppercase, apply titling for them
        # Else, assume that the specified case is intentional
        if request.POST['name'].islower() or request.POST['name'].isupper():
            new_user['name'] = request.POST['name'].title()
        else:
            new_user['name'] = request.POST['name']
        new_user['phone'] = request.POST['phone']
        new_user['email'] = request.POST['email'].lower()
        # Same capitalization on address as for name
        if request.POST['address'].islower() or request.POST['address'].isupper():
            request.session['registration']['address'] = request.POST['address'].title()
        else:
            request.session['registration']['address'] = request.POST['address']
        request.session['registration']['zipcode'] = request.POST['zipcode']
        if(request.POST.get('key') == 'on'):
            new_user['key'] = True

        try:
            new_user['dob'] = datetime.strptime(request.POST['dob'], "%d.%m.%Y")
            new_user['age'] = datetime.now().year - new_user['dob'].year
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

    contact_missing = request.GET.has_key(contact_missing_key)
    updateIndices(request)

    if not errors and request.POST.has_key('forward'):
        return HttpResponseRedirect(reverse("enrollment.views.household"))

    context = {'users': request.session['registration']['users'], 'user': user,
        'saved': saved, 'errors': errors, 'contact_missing': contact_missing,
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
    if not validate_user_contact(request.session['registration']['users']):
        return HttpResponseRedirect("%s?%s" % (reverse("enrollment.views.registration"), contact_missing_key))
    updateIndices(request)
    context = {'users': request.session['registration']['users'],
        'existing': request.session['registration'].get('existing', '')}
    return render(request, 'enrollment/household.html', context)

def verification(request):
    if not request.session.has_key('registration'):
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    if len(request.session['registration']['users']) == 0:
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    if not validate_user_contact(request.session['registration']['users']):
        return HttpResponseRedirect("%s?%s" % (reverse("enrollment.views.registration"), contact_missing_key))
    # Todo: verify that 'registration' is set in session
    request.session['registration']['existing'] = request.POST.get('existing', '')
    request.session['registration']['location'] = Zipcode.objects.get(zip_code=request.session['registration']['zipcode']).location
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
        'main': main, 'price_main': PRICE_MAIN, 'price_household': PRICE_HOUSEHOLD,
        'price_senior': PRICE_SENIOR, 'price_student': PRICE_STUDENT, 'price_school': PRICE_SCHOOL,
        'price_child': PRICE_CHILD, 'age_senior': AGE_SENIOR, 'age_main': AGE_MAIN,
        'age_student': AGE_STUDENT, 'age_school': AGE_SCHOOL}
    return render(request, 'enrollment/verification.html', context)

def payment(request):
    if not request.session.has_key('registration'):
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    if len(request.session['registration']['users']) == 0:
        return HttpResponseRedirect(reverse("enrollment.views.registration"))

    sum = 0
    for user in request.session['registration']['users']:
        sum += price_of(user['age'])

    now = datetime.now()
    if now.month >= MONTH_THRESHOLD:
        year = "%s, samt ut %s" % (now.year + 1, now.year)
    else:
        year = now.year

    t = loader.get_template('enrollment/payment-terminal.html')
    c = Context({'year': year, 'sum': sum})
    desc = t.render(c)

    r = requests.get(REGISTER_URL, params={
        'merchantId': settings.NETS_MERCHANT_ID,
        'token': settings.NETS_TOKEN,
        'orderNumber': 'TBD',
        'currencyCode': 'NOK',
        'amount': sum * 100,
        'orderDescription': desc,
        'redirectUrl': "http://%s%s" % (request.site, reverse("enrollment.views.result"))
    })

    request.session['transaction_id'] = etree.fromstring(r.text).find("TransactionId").text

    return HttpResponseRedirect("%s?merchantId=%s&transactionId=%s" % (
        TERMINAL_URL, settings.NETS_MERCHANT_ID, request.session['transaction_id']
    ))

def result(request):
    if request.GET['responseCode'] == 'OK':
        r = requests.get(PROCESS_URL, params={
            'merchantId': settings.NETS_MERCHANT_ID,
            'token': settings.NETS_TOKEN,
            'operation': 'SALE',
            'transactionId': request.session['transaction_id']
        })

        dom = etree.fromstring(r.text)
        code = dom.find(".//ResponseCode").text
        if code == 'OK':
            context = {'status': 'success'}
        else:
            context = {'status': 'fail'}
    else:
        context = {'status': 'cancel'}
    return render(request, 'enrollment/result.html', context)

def zipcode(request, code):
    location = Zipcode.objects.get(zip_code=code).location
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

    # Phone no. is non-empty (empty is allowed) and less than 8 chars
    # (allow >8, in case it's formatted with whitespace)
    if len(user['phone']) > 0 and len(user['phone']) < 8:
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
        Zipcode.objects.get(zip_code=zipcode)
    except Zipcode.DoesNotExist:
        return False

    # All tests passed!
    return True

# Check that at least one member has valid phone and email
def validate_user_contact(users):
    for user in users:
        # Phone no. is less than 8 chars (allow >8, in case it's formatted with whitespace)
        if len(user['phone']) < 8:
            continue

        # Email is doesn't match an email
        if(len(re.findall('.+@.+\..+', user['email'])) == 0):
            continue

        return True
    return False

def price_of(age):
    if age >= AGE_SENIOR:    return PRICE_SENIOR
    elif age >= AGE_MAIN:    return PRICE_MAIN
    elif age >= AGE_STUDENT: return PRICE_STUDENT
    elif age >= AGE_SCHOOL:  return PRICE_SCHOOL
    else:                    return PRICE_CHILD
