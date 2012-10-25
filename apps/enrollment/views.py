# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context, loader
from django.core.cache import cache
from django.db import transaction, connections

from core import validator
from sherpa2.models import Association
from user.models import Zipcode, FocusCountry
from focus.models import FocusZipcode, Enrollment, Actor, ActorAddress, Price
from enrollment.models import State

from datetime import datetime, timedelta
import requests
import re
import json
from lxml import etree
from urllib import quote_plus
from smtplib import SMTPDataError

# Number of days the temporary membership proof is valid
TEMPORARY_PROOF_VALIDITY = 14

KEY_PRICE = 100
FOREIGN_SHIPMENT_PRICE = 100

# GET parameters used for error handling
contact_missing_key = 'mangler-kontaktinfo'
invalid_main_member_key = 'ugyldig-hovedmedlem'
nonexistent_main_member_key = 'ikke-eksisterende-hovedmedlem'
no_main_member_key = 'mangler-hovedmedlem'
invalid_payment_method = 'ugyldig-betalingsmetode'
invalid_location = 'ugyldig-adresse'
invalid_existing = 'ugyldig-eksiserende-hovedmedlem'
too_many_underage = 'for-mange-ungdomsmedlemmer'

SMS_URL = "https://bedrift.telefonkatalogen.no/tk/sendsms.php?charset=utf-8&cellular=%s&msg=%s"
EMAIL_FROM = "Den Norske Turistforening <medlem@turistforeningen.no>"
EMAIL_SUBJECT_SINGLE = "Velkommen som medlem!"
EMAIL_SUBJECT_MULTIPLE = "Velkommen som medlemmer!"

# Hardcoded ages
AGE_SENIOR = 67
AGE_MAIN = 27
AGE_YOUTH = 19
AGE_SCHOOL = 13

# Registration states: 'registration' -> 'payment' -> 'complete'
# These are used in most views to know where the user came from and where
# they should be headed.

def index(request):
    return HttpResponseRedirect(reverse("enrollment.views.registration"))

def registration(request, user):
    request.session.modified = True
    if request.session.has_key('enrollment'):
        if request.session['enrollment']['state'] == 'payment':
            # Payment has been initiated but the user goes back to the registration page - why?
            # Maybe it failed, and they want to retry registration?
            # Reset the state and let them reinitiate payment when they're ready.
            request.session['enrollment']['state'] = 'registration'
        elif request.session['enrollment']['state'] == 'complete':
            # A previous registration has been completed, but a new one has been initiated.
            # Remove the old one and start over.
            del request.session['enrollment']

    # Check if this is a first-time registration (or start-over if the previous one was deleted)
    if not request.session.has_key('enrollment'):
        request.session['enrollment'] = {'users': [], 'state': 'registration'}
    elif not request.session['enrollment'].has_key('state'):
        # Temporary if-branch:
        # Since the 'state' key was recently added to the session dict,
        # add it for old users who revisit this page.
        request.session['enrollment']['state'] = 'registration'

    if user is not None:
        try:
            user = request.session['enrollment']['users'][int(user)]
        except IndexError:
            return HttpResponseRedirect(reverse('enrollment.views.registration'))

    errors = False
    if request.method == 'POST':
        new_user = {}
        # Titleize and strip whitespace before/after dash
        new_user['name'] = re.sub('\s*-\s*', '-', polite_title(request.POST['name'].strip()))
        new_user['phone'] = request.POST['phone'].strip()
        new_user['email'] = request.POST['email'].lower().strip()
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
                request.session['enrollment']['users'][int(request.POST['user'])] = new_user
            else:
                request.session['enrollment']['users'].append(new_user)

    contact_missing = request.GET.has_key(contact_missing_key)
    updateIndices(request.session)

    if not errors and request.POST.has_key('forward'):
        return HttpResponseRedirect(reverse("enrollment.views.household"))

    now = datetime.now()
    new_membership_year = datetime(year=now.year, month=settings.MEMBERSHIP_YEAR_START, day=now.day)

    context = {'users': request.session['enrollment']['users'], 'person': user,
        'errors': errors, 'contact_missing': contact_missing,
        'conditions': request.session['enrollment'].get('conditions', ''),
        'too_many_underage': request.GET.has_key(too_many_underage),
        'now': now, 'new_membership_year': new_membership_year}
    return render(request, 'enrollment/registration.html', context)

def remove(request, user):
    request.session.modified = True
    if not request.session.has_key('enrollment'):
        return HttpResponseRedirect(reverse("enrollment.views.registration"))

    # If the index is too high, ignore it and redirect the user back.
    # This should only happen if the user messes with back/forwards buttons in their browser,
    # and they'll at LEAST notice it the member list and price sum in the verification view.
    if len(request.session['enrollment']['users']) >= int(user) + 1:
        del request.session['enrollment']['users'][int(user)]
        if len(request.session['enrollment']['users']) == 0:
            del request.session['enrollment']
    return HttpResponseRedirect(reverse("enrollment.views.registration"))

def household(request):
    request.session.modified = True
    val = validate(request.session, require_location=False, require_existing=False)
    if val is not None:
        return val

    if request.session['enrollment']['state'] == 'payment':
        # Payment has been initiated but the user goes back here - why?
        # Reset the state and let them reinitiate payment when they're ready.
        request.session['enrollment']['state'] = 'registration'
    elif request.session['enrollment']['state'] == 'complete':
        # A previous registration has been completed, so why would the user come directly here?
        # Just redirect them back to registration which will restart a new registration.
        return HttpResponseRedirect(reverse("enrollment.views.registration"))

    request.session['enrollment']['conditions'] = True
    errors = request.GET.has_key(invalid_location)
    if request.method == 'POST':
        location = {}
        location['country'] = request.POST['country']
        location['address1'] = polite_title(request.POST['address1'])
        location['address2'] = polite_title(request.POST['address2'])
        location['address3'] = polite_title(request.POST['address3'])
        location['zipcode'] = request.POST['zipcode']
        location['city'] = request.POST.get('city', '')
        request.session['enrollment']['location'] = location
        request.session['enrollment']['yearbook'] = location['country'] != 'NO' and request.POST.has_key('yearbook')
        request.session['enrollment']['attempted_yearbook'] = False
        if request.session['enrollment']['yearbook'] and request.POST['existing'] != '':
            request.session['enrollment']['yearbook'] = False
            request.session['enrollment']['attempted_yearbook'] = True
        if request.POST.has_key('existing'):
            request.session['enrollment']['existing'] = request.POST['existing']

        if validate_location(request.session['enrollment']['location']):
            return HttpResponseRedirect(reverse('enrollment.views.verification'))
        else:
            errors = True

    main = False
    for user in request.session['enrollment']['users']:
        if user['age'] >= AGE_YOUTH:
            main = True
            break

    countries = FocusCountry.objects.all()
    countries_norway = countries.get(code='NO')
    countries_other_scandinavian = countries.filter(scandinavian=True).exclude(code='NO')
    countries_other = countries.filter(scandinavian=False)

    now = datetime.now()
    new_membership_year = datetime(year=now.year, month=settings.MEMBERSHIP_YEAR_START, day=now.day)

    updateIndices(request.session)
    context = {'users': request.session['enrollment']['users'],
        'location': request.session['enrollment'].get('location', ''),
        'existing': request.session['enrollment'].get('existing', ''),
        'invalid_existing': request.GET.has_key(invalid_existing),
        'countries_norway': countries_norway, 'main': main,
        'yearbook': request.session['enrollment'].get('yearbook', ''),
        'foreign_shipment_price': FOREIGN_SHIPMENT_PRICE,
        'countries_other_scandinavian': countries_other_scandinavian,
        'countries_other': countries_other, 'errors': errors,
        'now': now, 'new_membership_year': new_membership_year}
    return render(request, 'enrollment/household.html', context)

def existing(request):
    if not request.is_ajax():
        return HttpResponseRedirect(reverse('enrollment.views.household'))

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
    if age < AGE_YOUTH:
        return HttpResponse(json.dumps({'error': 'actor.too_young', 'age': age}))

    return HttpResponse(json.dumps({
        'name': "%s %s" % (actor.first_name, actor.last_name),
        'address': address.a1
    }))

def verification(request):
    request.session.modified = True
    val = validate(request.session, require_location=True, require_existing=True)
    if val is not None:
        return val

    if request.session['enrollment']['state'] == 'payment':
        # Payment has been initiated but the user goes back here - why?
        # Reset the state and let them reinitiate payment when they're ready.
        request.session['enrollment']['state'] = 'registration'
    elif request.session['enrollment']['state'] == 'complete':
        # A previous registration has been completed, so why would the user come directly here?
        # Just redirect them back to registration which will restart a new registration.
        return HttpResponseRedirect(reverse("enrollment.views.registration"))

    # If existing member is specified, save details and change to that address
    existing_name = ''
    if request.session['enrollment']['existing'] != '':
        actor = Actor.objects.get(actno=request.session['enrollment']['existing'])
        existing_name = "%s %s" % (actor.first_name, actor.last_name)
        address = ActorAddress.objects.get(actseqno=actor.seqno)
        request.session['enrollment']['location']['country'] = address.country
        if address.country == 'NO':
            request.session['enrollment']['location']['address1'] = address.a1
        elif address.country == 'DK' or address.country == 'SE':
            # Don't change the user-provided address.
            # The user might potentially provide a different address than the existing
            # member, which isn't allowed, but this is preferable to trying to parse the
            # existing address into zipcode, city etc.
            # In order to enforce the same address, the address logic for DK and SE in
            # add_focus_user would have to be rewritten.
            pass
        else:
            # Uppercase the country code as Focus doesn't use consistent casing
            request.session['enrollment']['location']['country'] = address.country.upper()
            request.session['enrollment']['location']['address1'] = address.a1
            request.session['enrollment']['location']['address2'] = address.a2
            request.session['enrollment']['location']['address3'] = address.a3

    if request.session['enrollment'].has_key('association'):
        del request.session['enrollment']['association']
    if request.session['enrollment']['location']['country'] == 'NO':
        # Get the city name for this zipcode
        request.session['enrollment']['location']['city'] = Zipcode.objects.get(zipcode=request.session['enrollment']['location']['zipcode']).location

        # Figure out which association this member belongs to
        association = cache.get('zipcode.association.%s' % request.session['enrollment']['location']['zipcode'])
        if association == None:
            zipcode = FocusZipcode.objects.get(zipcode=request.session['enrollment']['location']['zipcode'])
            association = Association.objects.get(focus_id=zipcode.main_association_id)
            cache.set('zipcode.association.%s' % request.session['enrollment']['location']['zipcode'], association, 60 * 60 * 24 * 7)
        request.session['enrollment']['association'] = association
    else:
        # Foreign members are registered with DNT Oslo og Omegn
        oslo_association_id = 2 # This is the current ID for that association
        association = cache.get('association.%s' % oslo_association_id)
        if association == None:
            association = Association.objects.get(id=oslo_association_id)
            cache.set('association.%s' % oslo_association_id, association, 60 * 60 * 24)
        request.session['enrollment']['association'] = association

    # Get the prices for that association
    price = cache.get('association.price.%s' % request.session['enrollment']['association'].focus_id)
    if price == None:
        price = Price.objects.get(association_id=request.session['enrollment']['association'].focus_id)
        cache.set('association.price.%s' % request.session['enrollment']['association'].focus_id, price, 60 * 60 * 24 * 7)
    request.session['enrollment']['price'] = price

    now = datetime.now()
    year = now.year
    next_year = now.month >= settings.MEMBERSHIP_YEAR_START
    new_membership_year = datetime(year=now.year, month=settings.MEMBERSHIP_YEAR_START, day=now.day)

    keycount = 0
    youth_or_older_count = 0
    main = None
    for user in request.session['enrollment']['users']:
        if main == None or (user['age'] < main['age'] and user['age'] >= AGE_YOUTH):
            # The cheapest option will be to set the youngest member, 19 or older, as main member
            main = user
        if user['age'] >= AGE_YOUTH:
            youth_or_older_count += 1
        if user.has_key('key'):
            keycount += 1
    keyprice = keycount * KEY_PRICE
    multiple_main = youth_or_older_count > 1
    updateIndices(request.session)
    context = {'users': request.session['enrollment']['users'],
        'country': FocusCountry.objects.get(code=request.session['enrollment']['location']['country']),
        'location': request.session['enrollment']['location'],
        'association': request.session['enrollment']['association'],
        'existing': request.session['enrollment']['existing'], 'existing_name': existing_name,
        'keycount': keycount, 'keyprice': keyprice, 'multiple_main': multiple_main,
        'main': main, 'year': year, 'next_year': next_year,
        'price': request.session['enrollment']['price'],
        'age_senior': AGE_SENIOR, 'age_main': AGE_MAIN, 'age_youth': AGE_YOUTH,
        'age_school': AGE_SCHOOL, 'invalid_main_member': request.GET.has_key(invalid_main_member_key),
        'nonexistent_main_member': request.GET.has_key(nonexistent_main_member_key),
        'no_main_member': request.GET.has_key(no_main_member_key),
        'yearbook': request.session['enrollment']['yearbook'],
        'attempted_yearbook': request.session['enrollment']['attempted_yearbook'],
        'foreign_shipment_price': FOREIGN_SHIPMENT_PRICE,
        'now': now, 'new_membership_year': new_membership_year}
    return render(request, 'enrollment/verification.html', context)

def payment_method(request):
    request.session.modified = True
    val = validate(request.session, require_location=True, require_existing=True)
    if val is not None:
        return val

    if request.session['enrollment']['state'] == 'payment':
        # Payment has been initiated but the user goes back here - why?
        # Reset the state and let them reinitiate payment when they're ready.
        request.session['enrollment']['state'] = 'registration'
    elif request.session['enrollment']['state'] == 'complete':
        # A previous registration has been completed, so why would the user come directly here?
        # Just redirect them back to registration which will restart a new registration.
        return HttpResponseRedirect(reverse("enrollment.views.registration"))

    request.session['enrollment']['main_member'] = request.POST.get('main-member', '')

    now = datetime.now()
    new_membership_year = datetime(year=now.year, month=settings.MEMBERSHIP_YEAR_START, day=now.day)

    context = {'invalid_payment_method': request.GET.has_key(invalid_payment_method),
        'card_available': State.objects.all()[0].card,
        'now': now, 'new_membership_year': new_membership_year}
    return render(request, 'enrollment/payment.html', context)

def payment(request):
    request.session.modified = True
    val = validate(request.session, require_location=True, require_existing=True)
    if val is not None:
        return val

    # If for some reason the user managed to POST 'card' as payment_method
    if not State.objects.all()[0].card and request.POST.get('payment_method', '') == 'card':
        return HttpResponseRedirect(reverse('enrollment.views.payment_method'))

    if request.session['enrollment']['state'] == 'registration':
        # All right, enter payment state
        request.session['enrollment']['state'] = 'payment'
    elif request.session['enrollment']['state'] == 'payment':
        # Already in payment state, skip payment and redirect forwards to processing
        if request.session['enrollment']['payment_method'] == 'invoice':
            return HttpResponseRedirect(reverse('enrollment.views.process_invoice'))
        elif request.session['enrollment']['payment_method'] == 'card':
            return HttpResponseRedirect("%s?merchantId=%s&transactionId=%s" % (
                settings.NETS_TERMINAL_URL, settings.NETS_MERCHANT_ID, request.session['enrollment']['transaction_id']
            ))
    elif request.session['enrollment']['state'] == 'complete':
        # Registration has already been completed, redirect forwards to results page
        return HttpResponseRedirect(reverse('enrollment.views.result'))

    if request.POST.get('payment_method', '') != 'card' and request.POST.get('payment_method', '') != 'invoice':
        return HttpResponseRedirect("%s?%s" % (reverse('enrollment.views.payment_method'), invalid_payment_method))
    request.session['enrollment']['payment_method'] = request.POST['payment_method']

    # Figure out who's a household-member, who's not, and who's the main member
    main = None
    linked_to = None
    if request.session['enrollment']['existing'] != '':
        # If a pre-existing main member is specified, everyone is household
        for user in request.session['enrollment']['users']:
            user['household'] = True
            user['yearbook'] = False
        linked_to = request.session['enrollment']['existing']
    elif request.session['enrollment']['main_member'] != '':
        # If the user specified someone, everyone except that member is household
        for user in request.session['enrollment']['users']:
            if user['index'] == int(request.session['enrollment']['main_member']):
                # Ensure that the user didn't circumvent the javascript limitations for selecting main member
                if user['age'] < AGE_YOUTH:
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
        # In this case, one or more members below youth age are registered,
        # so no main/household status applies.
        for user in request.session['enrollment']['users']:
            user['household'] = False
            user['yearbook'] = False
            # Verify that all members are below youth age
            if user['age'] >= AGE_YOUTH:
                return HttpResponseRedirect("%s?%s" % (reverse('enrollment.views.verification'), no_main_member_key))

    # Ok. We need the memberID of the main user, so add that user and generate its ID
    if main != None:
        # Note, main will always be None when an existing main member is specified
        main['id'] = add_focus_user(main['name'], main['dob'], main['age'], main['gender'],
            request.session['enrollment']['location'], main['phone'], main['email'],
            main['yearbook'], request.session['enrollment']['yearbook'], None,
            request.session['enrollment']['payment_method'], request.session['enrollment']['price'])
        linked_to = main['id']

    # Right, let's add the rest of them
    for user in request.session['enrollment']['users']:
        if user == main:
            continue
        user['id'] = add_focus_user(user['name'], user['dob'], user['age'], user['gender'],
            request.session['enrollment']['location'], user['phone'], user['email'],
            user['yearbook'], request.session['enrollment']['yearbook'],
            linked_to, request.session['enrollment']['payment_method'],
            request.session['enrollment']['price'])

    # Calculate the prices and membership type
    request.session['enrollment']['price_sum'] = 0
    for user in request.session['enrollment']['users']:
        user['price'] = price_of(user['age'], user['household'], request.session['enrollment']['price'])
        user['type'] = type_of(user['age'], user['household'])
        request.session['enrollment']['price_sum'] += user['price']
        if user.has_key('key'):
            request.session['enrollment']['price_sum'] += KEY_PRICE

    # Pay for yearbook if foreign
    if request.session['enrollment']['yearbook']:
        request.session['enrollment']['price_sum'] += FOREIGN_SHIPMENT_PRICE

    # If we're paying by invoice, skip ahead to invoice processing
    if request.session['enrollment']['payment_method'] == 'invoice':
        return HttpResponseRedirect(reverse('enrollment.views.process_invoice'))

    # Paying with card, move on.
    now = datetime.now()
    year = now.year
    next_year = now.month >= settings.MEMBERSHIP_YEAR_START

    # Infer order details based on (poor) conventions.
    if main != None:
        order_number = 'I_%s' % main['id']
        first_name = main['name'].split(' ')[0]
        last_name = main['name'].split(' ')[1:]
        email = main['email']
    else:
        found = False
        for user in request.session['enrollment']['users']:
            if user['age'] >= AGE_YOUTH:
                order_number = 'I_%s' % user['id']
                first_name = user['name'].split(' ')[0]
                last_name = user['name'].split(' ')[1:]
                email = user['email']
                found = True
                break
        if not found:
            order_number = 'I'
            for user in request.session['enrollment']['users']:
                order_number += '_%s' % user['id']
            # Just use the name of the first user.
            first_name = request.session['enrollment']['users'][0]['name'].split(' ')[0]
            last_name = request.session['enrollment']['users'][0]['name'].split(' ')[1:]
            email = request.session['enrollment']['users'][0]['email']

    t = loader.get_template('enrollment/payment-terminal.html')
    c = Context({'year': year, 'next_year': next_year})
    desc = t.render(c)

    # Send the transaction registration to Nets
    r = requests.get(settings.NETS_REGISTER_URL, params={
        'merchantId': settings.NETS_MERCHANT_ID,
        'token': settings.NETS_TOKEN,
        'orderNumber': order_number,
        'customerFirstName': first_name,
        'customerLastName': last_name,
        'customerEmail': email,
        'currencyCode': 'NOK',
        'amount': request.session['enrollment']['price_sum'] * 100,
        'orderDescription': desc,
        'redirectUrl': "http://%s%s" % (request.site, reverse("enrollment.views.process_card"))
    })

    # Sweet, almost done, now just send the user to complete the transaction
    request.session['enrollment']['transaction_id'] = etree.fromstring(r.text).find("TransactionId").text

    return HttpResponseRedirect("%s?merchantId=%s&transactionId=%s" % (
        settings.NETS_TERMINAL_URL, settings.NETS_MERCHANT_ID, request.session['enrollment']['transaction_id']
    ))

def process_invoice(request):
    request.session.modified = True
    if not request.session.has_key('enrollment'):
        return HttpResponseRedirect(reverse('enrollment.views.registration'))

    if request.session['enrollment']['state'] == 'registration':
        # Whoops, how did we get here without going through payment first? Redirect back.
        return HttpResponseRedirect(reverse('enrollment.views.payment_method'))
    elif request.session['enrollment']['state'] == 'payment':
        # Cool, this is where we want to be. Update the state to 'complete'
        request.session['enrollment']['state'] = 'complete'
    elif request.session['enrollment']['state'] == 'complete':
        # Registration has already been completed, redirect forwards to results page
        return HttpResponseRedirect(reverse('enrollment.views.result'))

    prepare_and_send_email(request.session['enrollment']['users'],
        request.session['enrollment']['association'],
        request.session['enrollment']['location'], 'invoice',
        request.session['enrollment']['price_sum'])

    request.session['enrollment']['result'] = 'invoice'
    return HttpResponseRedirect(reverse('enrollment.views.result'))

def process_card(request):
    request.session.modified = True
    if not request.session.has_key('enrollment'):
        return HttpResponseRedirect(reverse('enrollment.views.registration'))

    if request.session['enrollment']['state'] == 'registration':
        # Whoops, how did we get here without going through payment first? Redirect back.
        # Note, *this* makes it impossible to use a previously verified transaction id
        # on a *second* registration by skipping the payment view and going straight to this check.
        return HttpResponseRedirect(reverse('enrollment.views.payment_method'))
    elif request.session['enrollment']['state'] == 'payment':
        # Cool, this is where we want to be. Update the state to 'complete'
        request.session['enrollment']['state'] = 'complete'
    elif request.session['enrollment']['state'] == 'complete':
        # Registration has already been completed, redirect forwards to results page
        return HttpResponseRedirect(reverse('enrollment.views.result'))

    if request.GET['responseCode'] == 'OK':
        r = requests.get(settings.NETS_PROCESS_URL, params={
            'merchantId': settings.NETS_MERCHANT_ID,
            'token': settings.NETS_TOKEN,
            'operation': 'SALE',
            'transactionId': request.session['enrollment']['transaction_id']
        })
        dom = etree.fromstring(r.text)
        code = dom.find(".//ResponseCode").text
        if code == 'OK':
            # Register the payment in focus
            for user in request.session['enrollment']['users']:
                focus_user = Enrollment.objects.get(member_id=user['id'])
                focus_user.payed = True
                focus_user.save()
            prepare_and_send_email(request.session['enrollment']['users'],
                request.session['enrollment']['association'],
                request.session['enrollment']['location'], 'card',
                request.session['enrollment']['price_sum'])
            request.session['enrollment']['result'] = 'success'
        else:
            request.session['enrollment']['result'] = 'fail'
    else:
        request.session['enrollment']['result'] = 'cancel'
    return HttpResponseRedirect(reverse('enrollment.views.result'))

def result(request):
    request.session.modified = True
    if not request.session.has_key('enrollment'):
        return HttpResponseRedirect(reverse('enrollment.views.registration'))

    if request.session['enrollment']['state'] == 'registration':
        # Whoops, how did we get here without going through payment first? Redirect back.
        return HttpResponseRedirect(reverse('enrollment.views.payment_method'))
    elif request.session['enrollment']['state'] == 'payment':
        # Not done with payments, why is the user here? Redirect back to payment processing
        if request.session['enrollment']['payment_method'] == 'invoice':
            return HttpResponseRedirect(reverse('enrollment.views.process_invoice'))
        elif request.session['enrollment']['payment_method'] == 'card':
            return HttpResponseRedirect("%s?merchantId=%s&transactionId=%s" % (
                settings.NETS_TERMINAL_URL, settings.NETS_MERCHANT_ID, request.session['enrollment']['transaction_id']
            ))

    # Collect emails to a separate list for easier template formatting
    emails = []
    for user in request.session['enrollment']['users']:
        if user['email'] != '':
            emails.append(user['email'])

    now = datetime.now()
    new_membership_year = datetime(year=now.year, month=settings.MEMBERSHIP_YEAR_START, day=now.day)

    skip_header = request.session['enrollment']['result'] == 'invoice' or request.session['enrollment']['result'] == 'success'
    proof_validity_end = datetime.now() + timedelta(days=TEMPORARY_PROOF_VALIDITY)
    context = {'users': request.session['enrollment']['users'], 'skip_header': skip_header,
        'association': request.session['enrollment']['association'], 'proof_validity_end': proof_validity_end,
        'emails': emails, 'location': request.session['enrollment']['location'],
        'price_sum': request.session['enrollment']['price_sum'],
        'now': now, 'new_membership_year': new_membership_year}
    return render(request, 'enrollment/result/%s.html' % request.session['enrollment']['result'], context)

def sms(request):
    if not request.is_ajax():
        return HttpResponseRedirect(reverse('enrollment.views.result'))

    # Verify that this is a valid SMS request
    index = int(request.POST['index'])
    if request.session['enrollment']['state'] != 'complete':
        return HttpResponse(json.dumps({'error': 'enrollment_uncompleted'}))
    if request.session['enrollment']['location']['country'] != 'NO':
        return HttpResponse(json.dumps({'error': 'foreign_number'}))
    if request.session['enrollment']['users'][index].has_key('sms_sent'):
        return HttpResponse(json.dumps({'error': 'already_sent'}))
    number = request.session['enrollment']['users'][index]['phone']

    # Render the SMS template
    now = datetime.now()
    year = now.year
    next_year = now.month >= settings.MEMBERSHIP_YEAR_START
    t = loader.get_template('enrollment/result/sms.html')
    c = Context({'year': year, 'next_year': next_year,
        'users': request.session['enrollment']['users']})
    sms_message = t.render(c).encode('utf-8')

    # Send the message
    try:
        r = requests.get(SMS_URL % (quote_plus(number), quote_plus(sms_message)))
        # Check and return status
        status = re.findall('Status: .*', r.text)
        if len(status) == 0 or status[0][8:] != 'Meldingen er sendt':
            return HttpResponse(json.dumps({'error': 'service_fail', 'message': status[0][8:]}))
        request.session['enrollment']['users'][index]['sms_sent'] = True
        request.session.modified = True
        return HttpResponse(json.dumps({'error': 'none'}))
    except requests.ConnectionError:
        return HttpResponse(json.dumps({'error': 'connection_error'}))

def prepare_and_send_email(users, association, location, payment_method, price_sum):
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
    c = Context({'users': users, 'association': association, 'location': location,
        'proof_validity_end': proof_validity_end, 'price_sum': price_sum})
    message = t.render(c)
    try:
        send_mail(subject, message, EMAIL_FROM, email_recipients)
    except SMTPDataError:
        # Silently ignore this error. The user will have to do without email receipt.
        # TODO: Should probably log this error with detailed information.
        # Experienced this error when someone registered "har@ikke.no" as their address,
        # and got this message: (554, 'Message rejected: Address blacklisted.')
        pass

def updateIndices(session):
    i = 0
    for user in session['enrollment']['users']:
        user['index'] = i
        i += 1

def validate(session, require_location, require_existing):
    if not session.has_key('enrollment'):
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    if len(session['enrollment']['users']) == 0:
        return HttpResponseRedirect(reverse("enrollment.views.registration"))
    if not validate_youth_count(session['enrollment']['users']):
        return HttpResponseRedirect("%s?%s" % (reverse("enrollment.views.registration"), too_many_underage))
    if not validate_user_contact(session['enrollment']['users']):
        return HttpResponseRedirect("%s?%s" % (reverse("enrollment.views.registration"), contact_missing_key))
    if require_location:
        if not session['enrollment'].has_key('location') or not validate_location(session['enrollment']['location']):
            return HttpResponseRedirect("%s?%s" % (reverse("enrollment.views.household"), invalid_location))
    if require_existing:
        if session['enrollment']['existing'] != '' and not validate_existing(session['enrollment']['existing'], session['enrollment']['location']['zipcode'], session['enrollment']['location']['country']):
            return HttpResponseRedirect("%s?%s" % (reverse("enrollment.views.household"), invalid_existing))

def validate_user(user):
    # Name or address is empty
    if not validator.name(user['name']):
        return False

    # Gender is not set
    if user.get('gender', '') != 'm' and user.get('gender', '') != 'f':
        return False

    # Check phone number only if supplied
    if not validator.phone(user['phone'], req=False):
        return False

    # Email is non-empty (empty is allowed) and doesn't match an email
    if not validator.email(user['email'], req=False):
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

    # Birthyear is below 1900 (MSSQLs datetime datatype will barf)
    # Same as above, will be unicode when posted, but datetime when saved
    if isinstance(user['dob'], unicode):
        date_to_test = datetime.strptime(user['dob'], "%d.%m.%Y")
    else:
        date_to_test = user['dob']
    if date_to_test.year < 1900:
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
        if not Zipcode.objects.filter(zipcode=location['zipcode']).exists():
            return False

    # All tests passed!
    return True

# Check that at least one member has valid phone and email
def validate_user_contact(users):
    for user in users:
        if validator.phone(user['phone']) and validator.email(user['email']):
            return True
    return False

def validate_existing(id, zipcode, country):
    try:
        actor = Actor.objects.get(actno=id)
    except (Actor.DoesNotExist, ValueError):
        return False

    if datetime.now().year - actor.birth_date.year < AGE_YOUTH:
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
        if user['age'] >= AGE_YOUTH:
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
    elif age >= AGE_YOUTH:   return price.youth
    elif age >= AGE_SCHOOL:  return price.school
    else:                    return price.child

def type_of(age, household):
    if household and age >= AGE_YOUTH:   return 'Husstandsmedlem'
    elif age >= AGE_SENIOR:              return 'Honnørmedlem'
    elif age >= AGE_MAIN:                return 'Hovedmedlem'
    elif age >= AGE_YOUTH:               return 'Ungdomsmedlem'
    elif age >= AGE_SCHOOL:              return 'Skoleungdomsmedlem'
    else:                                return 'Barnemedlem'

def polite_title(str):
    # If the string is all lowercase or uppercase, apply titling for it
    # Else, assume that the specified case is intentional
    if str.islower() or str.isupper():
        return str.title()
    else:
        return str

def add_focus_user(name, dob, age, gender, location, phone, email, can_have_yearbook, wants_yearbook, linked_to, payment_method, price):
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
    else:
        # Foreigners need to pay shipment price for the yearbook, so if they match the
        # criteria to receive it, let them choose whether or not to get it
        yearbook = can_have_yearbook and wants_yearbook
        if yearbook:
            price += FOREIGN_SHIPMENT_PRICE
    if yearbook:
        yearbook_type = 152
    else:
        yearbook_type = ''

    adr1 = location['address1']
    if location['country'] == 'NO':
        adr2 = ''
        adr3 = ''
        zipcode = location['zipcode']
        city = location['city']
    elif location['country'] == 'DK' or location['country'] == 'SE':
        adr2 = ''
        adr3 = "%s-%s %s" % (location['country'], location['zipcode'], location['city'])
        zipcode = '0000'
        city = ''
    else:
        adr2 = location['address2']
        adr3 = location['address3']
        zipcode = '0000'
        city = ''

    # Fetch and increment memberid with stored procedure
    with transaction.commit_manually():
        cursor = connections['focus'].cursor()
        cursor.execute("exec sp_custTurist_updateMemberId")
        memberid = cursor.fetchone()[0]
        connections['focus'].commit_unless_managed()

    user = Enrollment(member_id=memberid, last_name=last_name, first_name=first_name, dob=dob,
        gender=gender, linked_to=linked_to, adr1=adr1, adr2=adr2, adr3=adr3,
        country=location['country'], phone='', email=email, receive_yearbook=yearbook, type=type,
        yearbook=yearbook_type, payment_method=payment_method, mob=phone, postnr=zipcode,
        poststed=city, language=language, totalprice=price)
    user.save()
    return memberid

def focus_payment_method_code(method):
    if method == 'card':      return 4
    elif method == 'invoice': return 1

def focus_type_of(age, household):
    if household and age >= AGE_YOUTH:
                             return 107
    elif age >= AGE_SENIOR:  return 103
    elif age >= AGE_MAIN:    return 101
    elif age >= AGE_YOUTH:   return 102
    elif age >= AGE_SCHOOL:  return 106
    else:                    return 105
    # 104 = Lifelong member
    # 108 = Old household entries, being phased out (use 107)
    # 109 = Lifelong household member

def focus_receive_yearbook(age, linked_to):
    if linked_to != '':
        return False
    elif age >= AGE_YOUTH:
        return True
    else:
        return False