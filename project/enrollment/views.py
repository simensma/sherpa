# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import Context, loader

from user.models import Zipcode, FocusUser, FocusActType

from datetime import datetime
import requests
import re
from lxml import etree

# From the start of this month, memberships are for the remaining year AND next year
# (1 = January, 12 = December)
MONTH_THRESHOLD = 10

KEY_PRICE = 100
contact_missing_key = 'mangler-kontaktinfo' # GET parameter used for error handling
invalid_main_member_key = 'ugyldig-hovedmedlem' # GET parameter used for error handling

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
        new_user['gender'] = request.POST.get('gender', '')
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
    updateIndices(request.session)

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
    updateIndices(request.session)
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
    if request.POST.has_key('existing'):
        request.session['registration']['existing'] = request.POST['existing']
    request.session['registration']['location'] = Zipcode.objects.get(zip_code=request.session['registration']['zipcode']).location

    now = datetime.now()
    year = now.year
    next_year = now.month >= MONTH_THRESHOLD

    keycount = 0
    student_or_older_count = 0
    main = None
    for user in request.session['registration']['users']:
        if(main == None or (user['age'] < main['age'] and user['age'] >= AGE_STUDENT)):
            # The cheapest option will be to set the youngest member, 19 or older, as main member
            main = user
        if(user['age'] >= AGE_STUDENT):
            student_or_older_count += 1
        if user.has_key('key'):
            keycount += 1
    keyprice = keycount * KEY_PRICE
    multiple_main = student_or_older_count > 1
    updateIndices(request.session)
    context = {'users': request.session['registration']['users'],
        'address': request.session['registration']['address'],
        'zipcode': request.session['registration']['zipcode'],
        'location': request.session['registration']['location'],
        'existing': request.session['registration']['existing'],
        'keycount': keycount, 'keyprice': keyprice, 'multiple_main': multiple_main,
        'main': main, 'year': year, 'next_year': next_year, 'price_main': PRICE_MAIN,
        'price_household': PRICE_HOUSEHOLD, 'price_senior': PRICE_SENIOR,
        'price_student': PRICE_STUDENT, 'price_school': PRICE_SCHOOL, 'price_child': PRICE_CHILD,
        'age_senior': AGE_SENIOR, 'age_main': AGE_MAIN, 'age_student': AGE_STUDENT,
        'age_school': AGE_SCHOOL, 'invalid_main_member': request.GET.has_key(invalid_main_member_key)}
    return render(request, 'enrollment/verification.html', context)

def payment(request):
    if not request.session.has_key('registration'):
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    if len(request.session['registration']['users']) == 0:
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    # Check that the requested main member is student-member or older.
    # This will (hopefully) only invalidate if someone manually "hacks" the post request.
    if request.session['registration']['existing'] == '':
        main = request.session['registration']['users'][int(request.POST['main-member'])]
        if main['age'] < AGE_STUDENT:
            return HttpResponseRedirect("%s?%s" % (reverse('enrollment.views.verification'), invalid_main_member_key))

    sum = 0
    existing = request.session['registration']['existing'] != ''
    for user in request.session['registration']['users']:
        household = existing or int(request.POST['main-member']) != user['index']
        sum += price_of(user['age'], household)

    now = datetime.now()
    year = now.year
    next_year = now.month >= MONTH_THRESHOLD

    t = loader.get_template('enrollment/payment-terminal.html')
    c = Context({'year': year, 'next_year': next_year})
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
            context = {'status': 'fail', 'message': dom.find(".//ResponseText").text}
    else:
        context = {'status': 'cancel'}
    return render(request, 'enrollment/result.html', context)

def zipcode(request, code):
    location = Zipcode.objects.get(zip_code=code).location
    return HttpResponse(location)

def updateIndices(session):
    i = 0
    for user in session['registration']['users']:
        user['index'] = i
        i += 1
    session.modified = True

def validate_user(user):
    # Name or address is empty
    if user['name'] == '':
        return False

    # Gender is not set
    if user.get('gender', '') != 'm' and user.get('gender', '') != 'f':
        return False

    # Check phone number only if supplied
    if len(user['phone']) > 0 and not validate_phone(user['phone']):
        return False

    # Email is non-empty (empty is allowed) and doesn't match an email
    if user['email'] != '' and not validate_email(user['email']):
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
        if validate_phone(user['phone']) and validate_email(user['email']):
            return True
    return False

def validate_phone(phone):
    # Phone no. is non-empty (empty is allowed) and less than 8 chars
    # (allow >8, in case it's formatted with whitespace)
    return len(phone) >= 8 and len(re.findall('[a-z]', phone, re.I)) == 0

def validate_email(email):
    # Email matches anything@anything.anything
    return len(re.findall('.+@.+\..+', email)) > 0

def price_of(age, household):
    if household:
        return min(price_of_age(age), PRICE_HOUSEHOLD)
    else:
        return price_of_age(age)

def price_of_age(age):
    if age >= AGE_SENIOR:    return PRICE_SENIOR
    elif age >= AGE_MAIN:    return PRICE_MAIN
    elif age >= AGE_STUDENT: return PRICE_STUDENT
    elif age >= AGE_SCHOOL:  return PRICE_SCHOOL
    else:                    return PRICE_CHILD

def add_focus_user(name, dob, age, gender, address, zip_code, city, phone, email, linked_to):
    first_name = ' '.join(name.split(' ')[:-1])
    last_name = name.split(' ')[-1]
    gender = 'M' if gender == 'm' else 'K'
    country = 'NO'
    language = 'nb_no'
    receive_yearbook = True # ???
    yearbook = 152
    type = focus_type_of(age, linked_to != None)
    pay_method = 4 # 4 = Card, 1 = invoice
    price = price_of(age, linked_to != None)
    linked_to = '' if linked_to == None else str(linked_to)

    # Possible race condition here if other apps use these tables
    # Transactions aren't used because:
    # 1. Django ORM-level transactions didn't seem to work (rollback had no effect)
    # 2. Raw execution *could* be used but avoids Djangos SQL-injection
    seq = FocusActType.objects.get(type='P')
    seq.next = seq.next + 7
    seq.save()
    user = FocusUser(member_id=seq.next, last_name=last_name, first_name=first_name, dob=dob,
        gender=gender, linked_to=linked_to, adr1=address, adr2='', adr3='', country=country,
        phone='', email=email, receive_yearbook=receive_yearbook, type=type, yearbook=yearbook,
        pay_method=pay_method, mob=phone, postnr=zip_code, poststed=city, language=language,
        totalprice=price, payed=True)
    user.save()

def focus_type_of(age, household):
    if household:            return 107
    elif age >= AGE_SENIOR:  return 103
    elif age >= AGE_MAIN:    return 101
    elif age >= AGE_STUDENT: return 102
    elif age >= AGE_SCHOOL:  return 106
    else:                    return 105
