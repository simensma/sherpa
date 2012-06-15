# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader

from group.models import Group
from user.models import Zipcode, FocusZipcode, FocusCountry, FocusUser, FocusActType, Actor, ActorAddress, FocusPrice

from datetime import datetime, timedelta
import requests
import re
import json
from lxml import etree
from urllib import quote_plus

# From the start of this month, memberships are for the remaining year AND next year
# (1 = January, 12 = December)
MONTH_THRESHOLD = 10

# Number of days the temporary membership proof is valid
TEMPORARY_PROOF_VALIDITY = 14

KEY_PRICE = 100
FOREIGN_YEARBOOK_PRICE = 100

# GET parameters used for error handling
contact_missing_key = 'mangler-kontaktinfo'
invalid_main_member_key = 'ugyldig-hovedmedlem'
nonexistent_main_member_key = 'ikke-eksisterende-hovedmedlem'
no_main_member_key = 'mangler-hovedmedlem'
invalid_payment_method = 'ugyldig-betalingsmetode'
invalid_location = 'ugyldig-adresse'
invalid_existing = 'ugyldig-eksiserende-hovedmedlem'
too_many_underage = 'for-mange-ungdomsmedlemmer'

REGISTER_URL = "https://epayment.bbs.no/Netaxept/Register.aspx"
TERMINAL_URL = "https://epayment.bbs.no/Terminal/default.aspx"
PROCESS_URL = "https://epayment.bbs.no/Netaxept/Process.aspx"

SMS_URL = "https://bedrift.telefonkatalogen.no/tk/sendsms.php?charset=utf-8&cellular=%s&msg=%s"
EMAIL_FROM = "Den Norske Turistforening <medlem@turistforeningen.no>"
EMAIL_SUBJECT_SINGLE = "Velkommen som medlem!"
EMAIL_SUBJECT_MULTIPLE = "Velkommen som medlemmer!"

# Hardcoded ages
AGE_SENIOR = 68
AGE_MAIN = 27
AGE_STUDENT = 19
AGE_SCHOOL = 13

def index(request):
    return HttpResponseRedirect(reverse("enrollment.views.registration"))

def registration(request, user):
    if not request.session.has_key('registration'):
        request.session['registration'] = {'users': []}

    if user is not None:
        user = request.session['registration']['users'][int(user)]

    errors = False
    if request.method == 'POST':
        new_user = {}
        # Titleize and strip whitespace before/after dash
        new_user['name'] = re.sub('\s*-\s*', '-', polite_title(request.POST['name']))
        new_user['phone'] = request.POST['phone']
        new_user['email'] = request.POST['email'].lower()
        new_user['gender'] = request.POST.get('gender', '')
        if request.POST.get('key') == 'on':
            new_user['key'] = True

        try:
            new_user['dob'] = datetime.strptime(request.POST['dob'], "%d.%m.%Y")
            new_user['age'] = datetime.now().year - new_user['dob'].year
        except ValueError:
            new_user['dob'] = None
            new_user['age'] = None

        if not validate_user(request.POST):
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

    contact_missing = request.GET.has_key(contact_missing_key)
    updateIndices(request.session)

    if not errors and request.POST.has_key('forward'):
        return HttpResponseRedirect(reverse("enrollment.views.household"))

    context = {'users': request.session['registration']['users'], 'user': user,
        'errors': errors, 'contact_missing': contact_missing,
        'conditions': request.session['registration'].get('conditions', ''),
        'too_many_underage': request.GET.has_key(too_many_underage)}
    return render(request, 'enrollment/registration.html', context)

def remove(request, user):
    del request.session['registration']['users'][int(user)]
    if len(request.session['registration']['users']) == 0:
        del request.session['registration']
    return HttpResponseRedirect(reverse("enrollment.views.registration"))

def household(request):
    val = validate(request.session, require_location=False, require_existing=False)
    if val is not None:
        return val

    request.session['registration']['conditions'] = True
    errors = request.GET.has_key(invalid_location)
    if request.method == 'POST':
        location = {}
        location['country'] = request.POST['country']
        location['address1'] = polite_title(request.POST['address1'])
        location['address2'] = polite_title(request.POST['address2'])
        location['address3'] = polite_title(request.POST['address3'])
        location['zipcode'] = request.POST['zipcode']
        location['city'] = request.POST.get('city', '')
        request.session['registration']['location'] = location
        request.session['registration']['yearbook'] = location['country'] != 'NO' and request.POST.has_key('yearbook')
        request.session['registration']['attempted_yearbook'] = False
        if request.session['registration']['yearbook'] and request.POST['existing'] != '':
            request.session['registration']['yearbook'] = False
            request.session['registration']['attempted_yearbook'] = True
        if request.POST.has_key('existing'):
            request.session['registration']['existing'] = request.POST['existing']

        if validate_location(request.session['registration']['location']):
            return HttpResponseRedirect(reverse('enrollment.views.verification'))
        else:
            errors = True
        request.session.modified = True

    main = False
    for user in request.session['registration']['users']:
        if user['age'] >= AGE_STUDENT:
            main = True
            break

    countries = FocusCountry.objects.all()
    countries_norway = countries.get(code='NO')
    countries_other_scandinavian = countries.filter(scandinavian=True).exclude(code='NO')
    countries_other = countries.filter(scandinavian=False)

    updateIndices(request.session)
    context = {'users': request.session['registration']['users'],
        'location': request.session['registration'].get('location', ''),
        'existing': request.session['registration'].get('existing', ''),
        'invalid_existing': request.GET.has_key(invalid_existing),
        'countries_norway': countries_norway, 'main': main,
        'yearbook': request.session['registration'].get('yearbook', ''),
        'foreign_yearbook_price': FOREIGN_YEARBOOK_PRICE,
        'countries_other_scandinavian': countries_other_scandinavian,
        'countries_other': countries_other, 'errors': errors}
    return render(request, 'enrollment/household.html', context)

def existing(request):
    # Note: This logic is duplicated in validate_existing()
    data = json.loads(request.POST['data'])
    if data['country'] == 'NO' and len(data['zipcode']) != 4:
        return HttpResponse(json.dumps({'error': 'bad_zipcode'}))
    try:
        actor = Actor.objects.get(actno=data['id'])
    except Actor.DoesNotExist:
        return HttpResponse(json.dumps({'error': 'actor.does_not_exist'}))
    except ValueError:
        return HttpResponse(json.dumps({'error': 'invalid_id'}))

    try:
        if data['country'] == 'NO':
            # Include zipcode for norwegian members
            address = ActorAddress.objects.get(actseqno=actor.seqno, zipcode=data['zipcode'], country=data['country'])
        else:
            address = ActorAddress.objects.get(actseqno=actor.seqno, country=data['country'])
    except ActorAddress.DoesNotExist:
        return HttpResponse(json.dumps({'error': 'actoraddress.does_not_exist'}))

    age = datetime.now().year - actor.birth_date.year
    if age < AGE_STUDENT:
        return HttpResponse(json.dumps({'error': 'actor.too_young', 'age': age}))

    return HttpResponse(json.dumps({
        'name': "%s %s" % (actor.first_name, actor.last_name),
        'address': address.a1
    }))

def verification(request):
    val = validate(request.session, require_location=True, require_existing=True)
    if val is not None:
        return val

    # If existing member is specified, save details and change to that address
    existing_name = ''
    if request.session['registration']['existing'] != '':
        actor = Actor.objects.get(actno=request.session['registration']['existing'])
        existing_name = "%s %s" % (actor.first_name, actor.last_name)
        address = ActorAddress.objects.get(actseqno=actor.seqno)
        request.session['registration']['location']['country'] = address.country
        if address.country == 'NO':
            request.session['registration']['location']['address1'] = address.a1
        elif address.country == 'DK' or address.country == 'SE':
            request.session['registration']['location']['address1'] = address.a1
            request.session['registration']['location']['zipcode'] = address.a2
            request.session['registration']['location']['city'] = address.a3
        else:
            request.session['registration']['location']['country'] = address.country
            request.session['registration']['location']['address1'] = address.a1
            request.session['registration']['location']['address2'] = address.a2
            request.session['registration']['location']['address3'] = address.a3

    if request.session['registration'].has_key('group'):
        del request.session['registration']['group']
    if request.session['registration']['location']['country'] == 'NO':
        # Get the city name for this zipcode
        request.session['registration']['location']['city'] = Zipcode.objects.get(zip_code=request.session['registration']['location']['zipcode']).location

        # Figure out which group this member belongs to
        zipcode = FocusZipcode.objects.get(postcode=request.session['registration']['location']['zipcode'])
        request.session['registration']['group'] = Group.objects.get(focus_id=zipcode.main_group_id)

        # Get the prices for that group
        request.session['registration']['price'] = FocusPrice.objects.get(group_id=request.session['registration']['group'].focus_id)
    else:
        # Foreign members are registered with DNT Oslo og Omegn, which has focus group ID 10
        request.session['registration']['group'] = Group.objects.get(focus_id=10)

        # Foreign member, use default prices.
        # Temporarily use the prices of group 10 (DNT Oslo og Omegn)
        request.session['registration']['price'] = FocusPrice.objects.get(group_id=10)

    now = datetime.now()
    year = now.year
    next_year = now.month >= MONTH_THRESHOLD

    keycount = 0
    student_or_older_count = 0
    main = None
    for user in request.session['registration']['users']:
        if main == None or (user['age'] < main['age'] and user['age'] >= AGE_STUDENT):
            # The cheapest option will be to set the youngest member, 19 or older, as main member
            main = user
        if user['age'] >= AGE_STUDENT:
            student_or_older_count += 1
        if user.has_key('key'):
            keycount += 1
    keyprice = keycount * KEY_PRICE
    multiple_main = student_or_older_count > 1
    updateIndices(request.session)
    context = {'users': request.session['registration']['users'],
        'country': FocusCountry.objects.get(code=request.session['registration']['location']['country']),
        'location': request.session['registration']['location'],
        'group': request.session['registration']['group'],
        'existing': request.session['registration']['existing'], 'existing_name': existing_name,
        'keycount': keycount, 'keyprice': keyprice, 'multiple_main': multiple_main,
        'main': main, 'year': year, 'next_year': next_year,
        'price': request.session['registration']['price'],
        'age_senior': AGE_SENIOR, 'age_main': AGE_MAIN, 'age_student': AGE_STUDENT,
        'age_school': AGE_SCHOOL, 'invalid_main_member': request.GET.has_key(invalid_main_member_key),
        'nonexistent_main_member': request.GET.has_key(nonexistent_main_member_key),
        'no_main_member': request.GET.has_key(no_main_member_key),
        'yearbook': request.session['registration']['yearbook'],
        'attempted_yearbook': request.session['registration']['attempted_yearbook'],
        'foreign_yearbook_price': FOREIGN_YEARBOOK_PRICE}
    return render(request, 'enrollment/verification.html', context)

def payment_method(request):
    val = validate(request.session, require_location=True, require_existing=True)
    if val is not None:
        return val

    request.session['registration']['main_member'] = request.POST.get('main-member', '')

    context = {'invalid_payment_method': request.GET.has_key(invalid_payment_method)}
    return render(request, 'enrollment/payment.html', context)

def payment(request):
    val = validate(request.session, require_location=True, require_existing=True)
    if val is not None:
        return val

    if request.POST.get('payment-method', '') != 'card' and request.POST.get('payment-method', '') != 'invoice':
        return HttpResponseRedirect("%s?%s" % (reverse('enrollment.views.payment_method'), invalid_payment_method))

    # Figure out who's a household-member, who's not, and who's the main member
    main = None
    linked_to = None
    if request.session['registration']['existing'] != '':
        # If a pre-existing main member is specified, everyone is household
        for user in request.session['registration']['users']:
            user['household'] = True
            user['yearbook'] = False
        linked_to = request.session['registration']['existing']
    elif request.session['registration']['main_member'] != '':
        # If the user specified someone, everyone except that member is household
        for user in request.session['registration']['users']:
            if user['index'] == int(request.session['registration']['main_member']):
                # Ensure that the user didn't circumvent the javascript limitations for selecting main member
                if user['age'] < AGE_STUDENT:
                    return HttpResponseRedirect("%s?%s" % (reverse('enrollment.views.verification'), invalid_main_member_key))
                user['household'] = False
                user['yearbook'] = True
                main = user
            else:
                user['household'] = True
                user['yearbook'] = False
        if main == None:
            # The specified main-member index doesn't exist
            return HttpResponseRedirect("%s?%s" % (reverse('enrollment.views.verification'), nonexistent_main_member_key))
    else:
        # In this case, one or more members below student age are registered,
        # so no main/household status applies.
        for user in request.session['registration']['users']:
            user['household'] = False
            user['yearbook'] = False
            # Verify that all members are below student age
            if user['age'] >= AGE_STUDENT:
                return HttpResponseRedirect("%s?%s" % (reverse('enrollment.views.verification'), no_main_member_key))

    # Ok. We need the memberID of the main user, so add that user and generate its ID
    if main != None:
        # Note, main will always be None when an existing main member is specified
        main['id'] = add_focus_user(main['name'], main['dob'], main['age'], main['gender'],
            request.session['registration']['location'], main['phone'], main['email'],
            main['yearbook'], None, request.POST['payment-method'],
            request.session['registration']['price'])
        linked_to = main['id']

    # Right, let's add the rest of them
    for user in request.session['registration']['users']:
        if user == main:
            continue
        user['id'] = add_focus_user(user['name'], user['dob'], user['age'], user['gender'],
            request.session['registration']['location'], user['phone'], user['email'],
            user['yearbook'], linked_to, request.POST['payment-method'],
            request.session['registration']['price'])

    # Cool. If we're paying by invoice, just forward to result page
    if request.POST['payment-method'] == 'invoice':
        return HttpResponseRedirect(reverse('enrollment.views.result', kwargs={'invoice': True}))

    # Paying with card. Calculate the order details
    sum = 0
    for user in request.session['registration']['users']:
        sum += price_of(user['age'], user['household'], request.session['registration']['price'])
        if user.has_key('key'):
            sum += KEY_PRICE

    # Pay for yearbook if foreign
    if request.session['registration']['yearbook']:
        sum += FOREIGN_YEARBOOK_PRICE

    now = datetime.now()
    year = now.year
    next_year = now.month >= MONTH_THRESHOLD

    # Infer order number
    if main != None:
        order_number = 'I_%s' % main['id']
    else:
        found = False
        for user in request.session['registration']['users']:
            if user['age'] >= AGE_STUDENT:
                order_number = 'I_%s' % user['id']
                found = True
                break
        if not found:
            order_number = 'I'
            for user in request.session['registration']['users']:
                order_number += '_%s' % user['id']

    t = loader.get_template('enrollment/payment-terminal.html')
    c = Context({'year': year, 'next_year': next_year})
    desc = t.render(c)

    # Send the transaction registration to Nets
    r = requests.get(REGISTER_URL, params={
        'merchantId': settings.NETS_MERCHANT_ID,
        'token': settings.NETS_TOKEN,
        'orderNumber': order_number,
        'currencyCode': 'NOK',
        'amount': sum * 100,
        'orderDescription': desc,
        'redirectUrl': "http://%s%s" % (request.site, reverse("enrollment.views.result", kwargs={'invoice': False}))
    })

    # Sweet, almost done, now just send the user to complete the transaction
    request.session['transaction_id'] = etree.fromstring(r.text).find("TransactionId").text
    request.session.modified = True

    return HttpResponseRedirect("%s?merchantId=%s&transactionId=%s" % (
        TERMINAL_URL, settings.NETS_MERCHANT_ID, request.session['transaction_id']
    ))

def result(request, invoice):
    users = request.session['registration']['users']
    group = request.session['registration']['group']
    location = request.session['registration']['location']
    if invoice:
        prepare_and_send_email(request.session['registration']['users'],
            request.session['registration']['group'],
            request.session['registration']['location'], 'invoice')
        result = 'invoice'
        skip_header = True
        request.session['registration_success'] = True
        del request.session['registration']
    elif request.GET['responseCode'] == 'OK':
        r = requests.get(PROCESS_URL, params={
            'merchantId': settings.NETS_MERCHANT_ID,
            'token': settings.NETS_TOKEN,
            'operation': 'SALE',
            'transactionId': request.session['transaction_id']
        })
        dom = etree.fromstring(r.text)
        code = dom.find(".//ResponseCode").text
        if code == 'OK':
            # Register the payment in focus
            for user in request.session['registration']['users']:
                focus_user = FocusUser.objects.get(member_id=user['id'])
                focus_user.payed = True
                focus_user.save()
            prepare_and_send_email(request.session['registration']['users'],
                request.session['registration']['group'],
                request.session['registration']['location'], 'card')
            result = 'success'
            skip_header = True
            request.session['registration_sms'] = {}
            request.session['registration_sms']['country'] = request.session['registration']['location']['country']
            request.session['registration_success'] = True
            request.session['registration_sms']['users'] = request.session['registration']['users']
            del request.session['registration']
        else:
            result = 'fail'
            skip_header = False
    else:
        result = 'cancel'
        skip_header = False

    # Collect emails to a separate list for easier template formatting
    emails = []
    for user in users:
        if user['email'] != '':
            emails.append(user['email'])

    proof_validity_end = datetime.now() + timedelta(days=TEMPORARY_PROOF_VALIDITY)
    context = {'users': users, 'skip_header': skip_header,
        'group': group, 'proof_validity_end': proof_validity_end, 'emails': emails,
        'location': location}
    return render(request, 'enrollment/result/%s.html' % result, context)

def sms(request):
    # Verify that this is a valid SMS request
    index = int(request.POST['index'])
    if request.session['registration_sms']['country'] != 'NO':
        return HttpResponse(json.dumps({'error': 'foreign_number'}))
    if not request.session.has_key('registration_success'):
        return HttpResponse(json.dumps({'error': 'not_registered'}))
    if request.session['registration_sms']['users'][index].has_key('sms_sent'):
        return HttpResponse(json.dumps({'error': 'already_sent'}))
    number = request.session['registration_sms']['users'][index]['phone']

    # Render the SMS template
    now = datetime.now()
    year = now.year
    next_year = now.month >= MONTH_THRESHOLD
    t = loader.get_template('enrollment/result/sms.html')
    c = Context({'year': year, 'next_year': next_year,
        'users': request.session['registration_sms']['users']})
    sms_message = t.render(c)

    # Send the message
    r = requests.get(SMS_URL % (quote_plus(number), quote_plus(sms_message)))

    # Check and return status
    status = re.findall('Status: .*', r.text)
    if len(status) == 0 or status[0][8:] != 'Meldingen er sendt':
        return HttpResponse(json.dumps({'error': 'service_fail', 'message': status[0][8:]}))
    request.session['registration_sms']['users'][index]['sms_sent'] = True
    return HttpResponse(json.dumps({'error': 'none'}))

def prepare_and_send_email(users, group, location, payment_method):
    email_recipients = []
    for user in users:
        if user['email'] != '':
            email_recipients.append(user['email'])
    if len(users) == 1:
        subject = EMAIL_SUBJECT_SINGLE
        template = 'email-%s-single.html' % payment_method
    else:
        subject = EMAIL_SUBJECT_MULTIPLE
        template = 'email-%s-multiple.html' % payment_method
    # proof_validity_end is not needed for the 'card' payment_method, but ignore that
    proof_validity_end = datetime.now() + timedelta(days=TEMPORARY_PROOF_VALIDITY)
    t = loader.get_template('enrollment/result/%s' % template)
    c = Context({'users': users, 'group': group, 'location': location,
        'proof_validity_end': proof_validity_end})
    message = t.render(c)
    send_mail(subject, message, EMAIL_FROM, email_recipients)

def zipcode(request, code):
    try:
        return HttpResponse(json.dumps({'location': Zipcode.objects.get(zip_code=code).location}))
    except Zipcode.DoesNotExist:
        return HttpResponse(json.dumps({'error': 'does_not_exist'}))

def updateIndices(session):
    i = 0
    for user in session['registration']['users']:
        user['index'] = i
        i += 1
    session.modified = True

def validate(session, require_location, require_existing):
    if not session.has_key('registration'):
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    if len(session['registration']['users']) == 0:
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    if not validate_youth_count(session['registration']['users']):
        return HttpResponseRedirect("%s?%s" % (reverse("enrollment.views.registration"), too_many_underage))
    if not validate_user_contact(session['registration']['users']):
        return HttpResponseRedirect("%s?%s" % (reverse("enrollment.views.registration"), contact_missing_key))
    if require_location:
        if not session['registration'].has_key('location') or not validate_location(session['registration']['location']):
            return HttpResponseRedirect("%s?%s" % (reverse("enrollment.views.household"), invalid_location))
    if require_existing:
        if session['registration']['existing'] != '' and not validate_existing(session['registration']['existing'], session['registration']['location']['zipcode'], session['registration']['location']['country']):
            return HttpResponseRedirect("%s?%s" % (reverse("enrollment.views.household"), invalid_existing))

def validate_user(user):
    # Name or address is empty
    if len(re.findall('.+\s.+', user['name'])) == 0:
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

def validate_location(location):
    # Country does not exist
    if not FocusCountry.objects.filter(code=location['country']).exists():
        return False

    # No address provided for other countries than Norway
    # (Some Norwegians actually don't have a street address)
    if location['country'] != 'NO':
        if location['address1'].strip() == '':
            return False

    # Require zipcode for all scandinavian countries
    if location['country'] == 'NO' or location['country'] == 'SE' or location['country'] == 'DK':
        if location['zipcode'].strip() == '':
            return False

    if location['country'] == 'SE' or location['country'] == 'DK':
        # No city provided
        if location['city'].strip() == '':
            return False

    if location['country'] == 'NO':
        # Zipcode does not exist
        if not Zipcode.objects.filter(zip_code=location['zipcode']).exists():
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

def validate_existing(id, zipcode, country):
    try:
        actor = Actor.objects.get(actno=id)
    except Actor.DoesNotExist:
        return False

    if datetime.now().year - actor.birth_date.year < AGE_STUDENT:
        return False

    if country == 'NO':
        if not ActorAddress.objects.filter(actseqno=actor.seqno, zipcode=zipcode, country=country).exists():
            return False
    else:
        if not ActorAddress.objects.filter(actseqno=actor.seqno, country=country).exists():
            return False
    return True

def validate_youth_count(users):
    # Based on order number length, which is 32.
    # MemberID is 7 chars, order number format is I[_<memberid>]+ so 4 users = 33 chars.
    if len(users) <= 3:
        return True
    at_least_one_main_member = False
    for user in users:
        if user['age'] >= AGE_STUDENT:
            at_least_one_main_member = True
            break
    return at_least_one_main_member

def price_of(age, household, price):
    if household:
        return min(price_of_age(age, price), price.household)
    else:
        return price_of_age(age, price)

def price_of_age(age, price):
    if age >= AGE_SENIOR:    return price.senior
    elif age >= AGE_MAIN:    return price.main
    elif age >= AGE_STUDENT: return price.student
    elif age >= AGE_SCHOOL:  return price.school
    else:                    return price.child

def polite_title(str):
    # If the string is all lowercase or uppercase, apply titling for it
    # Else, assume that the specified case is intentional
    if str.islower() or str.isupper():
        return str.title()
    else:
        return str

def add_focus_user(name, dob, age, gender, location, phone, email, yearbook, linked_to, payment_method, price):
    first_name = ' '.join(name.split(' ')[:-1])
    last_name = name.split(' ')[-1]
    gender = 'M' if gender == 'm' else 'K'
    language = 'nb_no'
    type = focus_type_of(age, linked_to != None)
    payment_method = focus_payment_method_code(payment_method)
    price = price_of(age, linked_to != None, price)
    linked_to = '' if linked_to == None else str(linked_to)
    if location['country'] == 'NO':
        # Override yearbook value for norwegians based on age and household status
        yearbook = focus_receive_yearbook(age, linked_to)
    if yearbook:
        yearbook_type = 152
    else:
        yearbook_type = ''

    adr1 = location['address1']
    if location['country'] == 'NO':
        adr2 = ''
        adr3 = ''
        zip_code = location['zipcode']
        city = location['city']
    elif location['country'] == 'DK' or location['country'] == 'SE':
        adr2 = "%s %s" % (location['zipcode'], location['city'])
        adr3 = ''
        zip_code = '0000'
        city = ''
    else:
        adr2 = location['address2']
        adr3 = location['address3']
        zip_code = '0000'
        city = ''

    # Possible race condition here if other apps use these tables
    # Transactions aren't used because:
    # 1. Django ORM-level transactions didn't seem to work (rollback had no effect)
    # 2. Raw execution *could* be used but avoids Djangos SQL-injection
    seq = FocusActType.objects.get(type='P')
    memberid = seq.next
    seq.next = memberid + 7
    seq.save()
    user = FocusUser(member_id=memberid, last_name=last_name, first_name=first_name, dob=dob,
        gender=gender, linked_to=linked_to, adr1=adr1, adr2=adr2, adr3=adr3,
        country=location['country'], phone='', email=email, receive_yearbook=yearbook, type=type,
        yearbook=yearbook_type, payment_method=payment_method, mob=phone, postnr=zip_code,
        poststed=city, language=language, totalprice=price)
    user.save()
    return memberid

def focus_payment_method_code(method):
    if method == 'card':      return 4
    elif method == 'invoice': return 1

def focus_type_of(age, household):
    if household and age >= AGE_MAIN and age < AGE_SENIOR:
                             return 107
    elif age >= AGE_SENIOR:  return 103
    elif age >= AGE_MAIN:    return 101
    elif age >= AGE_STUDENT: return 102
    elif age >= AGE_SCHOOL:  return 106
    else:                    return 105
    # 104 = Lifelong member
    # 108 = Old household entries, being phased out (use 107)
    # 109 = Lifelong household member

def focus_receive_yearbook(age, linked_to):
    if linked_to != '':
        return False
    elif age >= AGE_STUDENT:
        return True
    else:
        return False
