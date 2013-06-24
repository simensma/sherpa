# encoding: utf-8
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string
from django.core.cache import cache
from django.db import transaction, connections
from django.contrib import messages

from core import validator
from core.util import current_membership_year_start
from core.models import Zipcode, FocusCountry
from sherpa2.models import Association
from focus.models import FocusZipcode, Enrollment, Actor, ActorAddress, Price
from focus.util import get_membership_type_by_codename
from enrollment.models import State

from datetime import datetime, date, timedelta
import requests
import re
import json
import logging
import sys
from lxml import etree
from urllib import quote_plus
from smtplib import SMTPException

logger = logging.getLogger('sherpa')

# Number of days the temporary membership proof is valid
TEMPORARY_PROOF_VALIDITY = 14

KEY_PRICE = 100
FOREIGN_SHIPMENT_PRICE = 100

# GET parameters used for error handling (still a few remaining)
invalid_location = 'ugyldig-adresse'
invalid_existing = 'ugyldig-eksiserende-hovedmedlem'

EMAIL_FROM = "Den Norske Turistforening <medlem@turistforeningen.no>"
EMAIL_SUBJECT_SINGLE = "Velkommen som medlem!"
EMAIL_SUBJECT_MULTIPLE = "Velkommen som medlemmer!"

FOCUS_PAYMENT_METHOD_CODES = {
    'card': 4,
    'invoice': 1
}

# Hardcoded ages
AGE_SENIOR = 67
AGE_MAIN = 27
AGE_YOUTH = 19
AGE_SCHOOL = 13

# Registration states: 'registration' -> 'payment' -> 'complete'
# These are used in most views to know where the user came from and where
# they should be headed.

def index(request):
    return redirect("enrollment.views.registration")

def registration(request, user):
    request.session.modified = True
    if 'enrollment' in request.session:
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
    if not 'enrollment' in request.session:
        request.session['enrollment'] = {'users': [], 'state': 'registration'}
    elif not 'state' in request.session['enrollment']:
        # Temporary if-branch:
        # Since the 'state' key was recently added to the session dict,
        # add it for old users who revisit this page.
        request.session['enrollment']['state'] = 'registration'

    if user is not None:
        try:
            user = request.session['enrollment']['users'][int(user)]
        except IndexError:
            return redirect('enrollment.views.registration')

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
            if 'user' in request.POST:
                index = int(request.POST['user'])
                user = new_user
                user['index'] = index
            else:
                user = new_user
        else:
            if 'user' in request.POST:
                request.session['enrollment']['users'][int(request.POST['user'])] = new_user
            else:
                request.session['enrollment']['users'].append(new_user)

    updateIndices(request.session)

    if not errors and 'forward' in request.POST:
        return redirect("enrollment.views.household")

    today = date.today()
    new_membership_year = current_membership_year_start()

    context = {
        'users': request.session['enrollment']['users'],
        'person': user,
        'errors': errors,
        'conditions': request.session['enrollment'].get('conditions', ''),
        'today': today,
        'new_membership_year': new_membership_year
    }
    return render(request, 'main/enrollment/registration.html', context)

def remove(request, user):
    request.session.modified = True
    if not 'enrollment' in request.session:
        return redirect("enrollment.views.registration")

    # If the index is too high, ignore it and redirect the user back.
    # This should only happen if the user messes with back/forwards buttons in their browser,
    # and they'll at LEAST notice it the member list and price sum in the verification view.
    if len(request.session['enrollment']['users']) >= int(user) + 1:
        del request.session['enrollment']['users'][int(user)]
        if len(request.session['enrollment']['users']) == 0:
            del request.session['enrollment']
    return redirect("enrollment.views.registration")

def household(request):
    request.session.modified = True
    val = validate(request, require_location=False, require_existing=False)
    if val is not None:
        return val

    if request.session['enrollment']['state'] == 'payment':
        # Payment has been initiated but the user goes back here - why?
        # Reset the state and let them reinitiate payment when they're ready.
        request.session['enrollment']['state'] = 'registration'
    elif request.session['enrollment']['state'] == 'complete':
        # A previous registration has been completed, so why would the user come directly here?
        # Just redirect them back to registration which will restart a new registration.
        return redirect("enrollment.views.registration")

    request.session['enrollment']['conditions'] = True
    errors = invalid_location in request.GET
    if request.method == 'POST':
        location = {}
        location['country'] = request.POST['country']
        location['address1'] = polite_title(request.POST['address1'])
        location['address2'] = polite_title(request.POST['address2'])
        location['address3'] = polite_title(request.POST['address3'])
        location['zipcode'] = request.POST['zipcode']
        location['area'] = request.POST.get('area', '')
        request.session['enrollment']['location'] = location
        request.session['enrollment']['yearbook'] = location['country'] != 'NO' and 'yearbook' in request.POST
        request.session['enrollment']['attempted_yearbook'] = False
        if request.session['enrollment']['yearbook'] and request.POST['existing'] != '':
            request.session['enrollment']['yearbook'] = False
            request.session['enrollment']['attempted_yearbook'] = True
        if 'existing' in request.POST:
            request.session['enrollment']['existing'] = request.POST['existing']

        if validate_location(request.session['enrollment']['location']):
            if request.session['enrollment']['location']['country'] != 'NO':
                return redirect('enrollment.views.verification')
            else:
                try:
                    focus_zipcode = FocusZipcode.objects.get(zipcode=request.session['enrollment']['location']['zipcode'])
                    association = Association.objects.get(focus_id=focus_zipcode.main_association_id)
                    return redirect('enrollment.views.verification')
                except FocusZipcode.DoesNotExist:
                    # We know that this zipcode exists in Zipcode, because validate_location validated, and it checks for that
                    logger.warning(u"Postnummer finnes i Zipcode, men ikke i Focus!",
                        exc_info=sys.exc_info(),
                        extra={
                            'request': request,
                            'postnummer': request.session['enrollment']['location']['zipcode']
                        }
                    )
                    messages.error(request, 'focus_zipcode_missing')
                except Association.DoesNotExist:
                    logger.warning(u"Focus-postnummer mangler foreningstilknytning!",
                        exc_info=sys.exc_info(),
                        extra={'request': request}
                    )
                    messages.error(request, 'focus_zipcode_missing')
        else:
            errors = True

    main = False
    for user in request.session['enrollment']['users']:
        if user['age'] >= AGE_YOUTH:
            main = True
            break

    today = date.today()
    new_membership_year = current_membership_year_start()

    updateIndices(request.session)
    context = {
        'users': request.session['enrollment']['users'],
        'location': request.session['enrollment'].get('location', ''),
        'existing': request.session['enrollment'].get('existing', ''),
        'invalid_existing': invalid_existing in request.GET,
        'countries': FocusCountry.get_sorted(),
        'main': main,
        'yearbook': request.session['enrollment'].get('yearbook', ''),
        'foreign_shipment_price': FOREIGN_SHIPMENT_PRICE,
        'errors': errors,
        'today': today,
        'new_membership_year': new_membership_year
    }
    return render(request, 'main/enrollment/household.html', context)

def existing(request):
    if not request.is_ajax():
        return redirect('enrollment.views.household')

    # Note: This logic is duplicated in validate_existing()
    data = json.loads(request.POST['data'])
    if data['country'] == 'NO' and len(data['zipcode']) != 4:
        return HttpResponse(json.dumps({'error': 'bad_zipcode'}))
    try:
        actor = Actor.objects.get(memberid=data['id'])
    except Actor.DoesNotExist:
        return HttpResponse(json.dumps({'error': 'actor.does_not_exist'}))
    except ValueError:
        return HttpResponse(json.dumps({'error': 'invalid_id'}))

    try:
        if data['country'] == 'NO':
            # Include zipcode for norwegian members
            address = ActorAddress.objects.get(actor=actor.id, zipcode=data['zipcode'], country_code=data['country'])
        else:
            address = ActorAddress.objects.get(actor=actor.id, country_code=data['country'])
    except ActorAddress.DoesNotExist:
        return HttpResponse(json.dumps({'error': 'actoraddress.does_not_exist'}))

    age = datetime.now().year - actor.birth_date.year
    if age < AGE_YOUTH:
        return HttpResponse(json.dumps({'error': 'actor.too_young', 'age': age}))

    if actor.is_household_member():
        return HttpResponse(json.dumps({'error': 'actor.is_household_member'}))

    return HttpResponse(json.dumps({
        'name': "%s %s" % (actor.first_name, actor.last_name),
        'address': address.a1
    }))

def verification(request):
    request.session.modified = True
    val = validate(request, require_location=True, require_existing=True)
    if val is not None:
        return val

    if request.session['enrollment']['state'] == 'payment':
        # Payment has been initiated but the user goes back here - why?
        # Reset the state and let them reinitiate payment when they're ready.
        request.session['enrollment']['state'] = 'registration'
    elif request.session['enrollment']['state'] == 'complete':
        # A previous registration has been completed, so why would the user come directly here?
        # Just redirect them back to registration which will restart a new registration.
        return redirect("enrollment.views.registration")

    # If existing member is specified, save details and change to that address
    existing_name = ''
    if request.session['enrollment']['existing'] != '':
        actor = Actor.objects.get(memberid=request.session['enrollment']['existing'])
        existing_name = "%s %s" % (actor.first_name, actor.last_name)
        request.session['enrollment']['location']['country'] = actor.get_clean_address().country.code
        if actor.get_clean_address().country.code == 'NO':
            request.session['enrollment']['location']['address1'] = actor.get_clean_address().field1
        elif actor.get_clean_address().country.code == 'DK' or actor.get_clean_address().country.code == 'SE':
            # Don't change the user-provided address.
            # The user might potentially provide a different address than the existing
            # member, which isn't allowed, but this is preferable to trying to parse the
            # existing address into zipcode, area etc.
            # In order to enforce the same address, the address logic for DK and SE in
            # add_focus_user would have to be rewritten.
            pass
        else:
            # Uppercase the country code as Focus doesn't use consistent casing
            request.session['enrollment']['location']['country'] = actor.get_clean_address().country.code
            request.session['enrollment']['location']['address1'] = actor.get_clean_address().field1
            request.session['enrollment']['location']['address2'] = actor.get_clean_address().field2
            request.session['enrollment']['location']['address3'] = actor.get_clean_address().field3

    # Get the area name for this zipcode
    if request.session['enrollment']['location']['country'] == 'NO':
        request.session['enrollment']['location']['area'] = Zipcode.objects.get(zipcode=request.session['enrollment']['location']['zipcode']).area

    # Figure out which association this member/these members will belong to
    if request.session['enrollment']['existing'] != '':
        # Use main members' association if applicable
        focus_association_id = Actor.objects.get(memberid=request.session['enrollment']['existing']).main_association_id
        association = cache.get('focus.association_sherpa2.%s' % focus_association_id)
        if association is None:
            association = Association.objects.get(focus_id=focus_association_id)
            cache.set('focus.association_sherpa2.%s' % focus_association_id, association, 60 * 60 * 24 * 7)
    else:
        if request.session['enrollment']['location']['country'] == 'NO':
            focus_association_id = cache.get('focus.zipcode_association.%s' % request.session['enrollment']['location']['zipcode'])
            if focus_association_id is None:
                focus_association_id = FocusZipcode.objects.get(zipcode=request.session['enrollment']['location']['zipcode']).main_association_id
                cache.set('focus.zipcode_association.%s' % request.session['enrollment']['location']['zipcode'], focus_association_id, 60 * 60 * 24 * 7)
            association = cache.get('focus.association_sherpa2.%s' % focus_association_id)
            if association is None:
                association = Association.objects.get(focus_id=focus_association_id)
                cache.set('focus.association_sherpa2.%s' % focus_association_id, association, 60 * 60 * 24 * 7)
        else:
            # Foreign members are registered with DNT Oslo og Omegn
            oslo_association_id = 2 # This is the current ID for that association
            association = cache.get('association_sherpa2.%s' % oslo_association_id)
            if association is None:
                association = Association.objects.get(id=oslo_association_id)
                cache.set('association_sherpa2.%s' % oslo_association_id, association, 60 * 60 * 24)
    request.session['enrollment']['association'] = association

    # Get the prices for that association
    price = cache.get('association.price.%s' % request.session['enrollment']['association'].focus_id)
    if price is None:
        price = Price.objects.get(association_id=request.session['enrollment']['association'].focus_id)
        cache.set('association.price.%s' % request.session['enrollment']['association'].focus_id, price, 60 * 60 * 24 * 7)
    request.session['enrollment']['price'] = price

    today = date.today()
    new_membership_year = current_membership_year_start()

    keycount = 0
    youth_or_older_count = 0
    main = None
    for user in request.session['enrollment']['users']:
        if main is None or (user['age'] < main['age'] and user['age'] >= AGE_YOUTH):
            # The cheapest option will be to set the youngest member, 19 or older, as main member
            main = user
        if user['age'] >= AGE_YOUTH:
            youth_or_older_count += 1
        if 'key' in user:
            keycount += 1
    keyprice = keycount * KEY_PRICE
    multiple_main = youth_or_older_count > 1
    updateIndices(request.session)
    context = {
        'users': request.session['enrollment']['users'],
        'country': FocusCountry.objects.get(code=request.session['enrollment']['location']['country']),
        'location': request.session['enrollment']['location'],
        'association': request.session['enrollment']['association'],
        'existing': request.session['enrollment']['existing'],
        'existing_name': existing_name,
        'keycount': keycount,
        'keyprice': keyprice,
        'multiple_main': multiple_main,
        'main': main,
        'price': request.session['enrollment']['price'],
        'age_senior': AGE_SENIOR,
        'age_main': AGE_MAIN,
        'age_youth': AGE_YOUTH,
        'age_school': AGE_SCHOOL,
        'membership_type_names': {
            'senior': get_membership_type_by_codename('senior')['name'],
            'main': get_membership_type_by_codename('main')['name'],
            'youth': get_membership_type_by_codename('youth')['name'],
            'school': get_membership_type_by_codename('school')['name'],
            'household': get_membership_type_by_codename('household')['name'],
        },
        'yearbook': request.session['enrollment']['yearbook'],
        'attempted_yearbook': request.session['enrollment']['attempted_yearbook'],
        'foreign_shipment_price': FOREIGN_SHIPMENT_PRICE,
        'today': today,
        'new_membership_year': new_membership_year
    }
    return render(request, 'main/enrollment/verification.html', context)

def payment_method(request):
    request.session.modified = True
    val = validate(request, require_location=True, require_existing=True)
    if val is not None:
        return val

    if request.session['enrollment']['state'] == 'payment':
        # Payment has been initiated but the user goes back here - why?
        # Reset the state and let them reinitiate payment when they're ready.
        request.session['enrollment']['state'] = 'registration'
    elif request.session['enrollment']['state'] == 'complete':
        # A previous registration has been completed, so why would the user come directly here?
        # Just redirect them back to registration which will restart a new registration.
        return redirect("enrollment.views.registration")

    request.session['enrollment']['main_member'] = request.POST.get('main-member', '')

    today = date.today()
    new_membership_year = current_membership_year_start()

    context = {
        'card_available': State.objects.all()[0].card,
        'today': today,
        'new_membership_year': new_membership_year
    }
    return render(request, 'main/enrollment/payment.html', context)

def payment(request):
    request.session.modified = True
    val = validate(request, require_location=True, require_existing=True)
    if val is not None:
        return val

    # If for some reason the user managed to POST 'card' as payment_method
    if not State.objects.all()[0].card and request.POST.get('payment_method', '') == 'card':
        return redirect('enrollment.views.payment_method')

    if request.session['enrollment']['state'] == 'registration':
        # All right, enter payment state
        request.session['enrollment']['state'] = 'payment'
    elif request.session['enrollment']['state'] == 'payment':
        # Already in payment state, redirect them forwards to processing
        if request.session['enrollment']['payment_method'] == 'invoice':
            return redirect('enrollment.views.process_invoice')
        elif request.session['enrollment']['payment_method'] == 'card':
            # Let's check for a transaction id first
            if 'transaction_id' in request.session['enrollment']:
                # Yeah, it's there. Skip payment and redirect forwards to processing
                return redirect("%s?merchantId=%s&transactionId=%s" % (
                    settings.NETS_TERMINAL_URL, settings.NETS_MERCHANT_ID, request.session['enrollment']['transaction_id']
                ))
            else:
                # No transaction id - maybe a problem occured during payment.
                # Assume payment failed and just redo it - if something failed, we'll know
                # through logs and hopefully discover any double-payments
                pass
    elif request.session['enrollment']['state'] == 'complete':
        # Registration has already been completed, redirect forwards to results page
        return redirect('enrollment.views.result')

    if request.POST.get('payment_method', '') != 'card' and request.POST.get('payment_method', '') != 'invoice':
        messages.error(request, 'invalid_payment_method')
        return redirect('enrollment.views.payment_method')
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
                    messages.error(request, 'invalid_main_member')
                    return redirect('enrollment.views.verification')
                user['household'] = False
                user['yearbook'] = True
                main = user
            else:
                user['household'] = True
                user['yearbook'] = False
        if main is None:
            # The specified main-member index doesn't exist
            messages.error(request, 'nonexistent_main_member')
            return redirect('enrollment.views.verification')
    else:
        # In this case, one or more members below youth age are registered,
        # so no main/household status applies.
        for user in request.session['enrollment']['users']:
            user['household'] = False
            user['yearbook'] = False
            # Verify that all members are below youth age
            if user['age'] >= AGE_YOUTH:
                messages.error(request, 'no_main_member')
                return redirect('enrollment.views.verification')

    # Ok. We need the memberID of the main user, so add that user and generate its ID
    if main is not None:
        # Note, main will always be None when an existing main member is specified
        main['id'] = add_focus_user(
            main['name'],
            main['dob'],
            main['age'],
            main['gender'],
            request.session['enrollment']['location'],
            main['phone'],
            main['email'],
            main['yearbook'],
            request.session['enrollment']['yearbook'],
            None,
            request.session['enrollment']['payment_method'],
            request.session['enrollment']['price']
        )
        linked_to = main['id']

    # Right, let's add the rest of them
    for user in request.session['enrollment']['users']:
        if user == main:
            continue
        user['id'] = add_focus_user(
            user['name'],
            user['dob'],
            user['age'],
            user['gender'],
            request.session['enrollment']['location'],
            user['phone'],
            user['email'],
            user['yearbook'],
            request.session['enrollment']['yearbook'],
            linked_to,
            request.session['enrollment']['payment_method'],
            request.session['enrollment']['price']
        )

    # Calculate the prices and membership type
    request.session['enrollment']['price_sum'] = 0
    for user in request.session['enrollment']['users']:
        user['price'] = price_of(user['age'], user['household'], request.session['enrollment']['price'])
        user['type'] = type_of(user['age'], user['household'])
        request.session['enrollment']['price_sum'] += user['price']
        if 'key' in user:
            request.session['enrollment']['price_sum'] += KEY_PRICE

    # Pay for yearbook if foreign
    if request.session['enrollment']['yearbook']:
        request.session['enrollment']['price_sum'] += FOREIGN_SHIPMENT_PRICE

    # If we're paying by invoice, skip ahead to invoice processing
    if request.session['enrollment']['payment_method'] == 'invoice':
        return redirect('enrollment.views.process_invoice')

    # Paying with card, move on.
    today = date.today()
    year = today.year
    next_year = today >= current_membership_year_start()

    # Infer order details based on (poor) conventions.
    if main is not None:
        order_number = 'I_%s' % main['id']
        first_name, last_name = main['name'].rsplit(' ', 1)
        email = main['email']
    else:
        found = False
        for user in request.session['enrollment']['users']:
            if user['age'] >= AGE_YOUTH:
                order_number = 'I_%s' % user['id']
                first_name, last_name = user['name'].rsplit(' ', 1)
                email = user['email']
                found = True
                break
        if not found:
            order_number = 'I'
            for user in request.session['enrollment']['users']:
                order_number += '_%s' % user['id']
            # Just use the name of the first user.
            first_name, last_name = request.session['enrollment']['users'][0]['name'].rsplit(' ', 1)
            email = request.session['enrollment']['users'][0]['email']

    context = Context({'year': year, 'next_year': next_year})
    desc = render_to_string('main/enrollment/payment-terminal.html', context)

    # Send the transaction registration to Nets
    try:
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
            'redirectUrl': "http://%s%s" % (request.site.domain, reverse("enrollment.views.process_card"))
        })
    except requests.ConnectionError as e:
        logger.warning(e.message,
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        messages.error(request, 'nets_register_connection_error')
        return redirect('enrollment.views.payment_method')

    # Sweet, almost done, now just send the user to complete the transaction
    # Consider handling errors here (unexpected XML response or connection error)
    # We recieved a random "Unable to create setup string" message once, ignoring it for now
    response = r.text.encode('utf-8')
    request.session['enrollment']['transaction_id'] = etree.fromstring(response).find("TransactionId").text

    return redirect("%s?merchantId=%s&transactionId=%s" % (
        settings.NETS_TERMINAL_URL, settings.NETS_MERCHANT_ID, request.session['enrollment']['transaction_id']
    ))

def process_invoice(request):
    request.session.modified = True
    if not 'enrollment' in request.session:
        return redirect('enrollment.views.registration')

    if request.session['enrollment']['state'] == 'registration':
        # Whoops, how did we get here without going through payment first? Redirect back.
        return redirect('enrollment.views.payment_method')
    elif request.session['enrollment']['state'] == 'payment':
        # Cool, this is where we want to be. Update the state to 'complete'
        request.session['enrollment']['state'] = 'complete'
    elif request.session['enrollment']['state'] == 'complete':
        # Registration has already been completed, redirect forwards to results page
        return redirect('enrollment.views.result')

    prepare_and_send_email(
        request,
        request.session['enrollment']['users'],
        request.session['enrollment']['association'],
        request.session['enrollment']['location'],
        'invoice',
        request.session['enrollment']['price_sum'])

    request.session['enrollment']['result'] = 'success_invoice'
    return redirect('enrollment.views.result')

def process_card(request):
    request.session.modified = True
    if not 'enrollment' in request.session:
        return redirect('enrollment.views.registration')

    if request.session['enrollment']['state'] == 'registration':
        # Whoops, how did we get here without going through payment first? Redirect back.
        # Note, *this* makes it impossible to use a previously verified transaction id
        # on a *second* registration by skipping the payment view and going straight to this check.
        return redirect('enrollment.views.payment_method')
    elif request.session['enrollment']['state'] == 'payment':
        # Cool, this is where we want to be. Update the state to 'complete'
        request.session['enrollment']['state'] = 'complete'
    elif request.session['enrollment']['state'] == 'complete':
        # Registration has already been completed, redirect forwards to results page
        return redirect('enrollment.views.result')

    if request.GET['responseCode'] == 'OK':
        try:
            r = requests.get(settings.NETS_PROCESS_URL, params={
                'merchantId': settings.NETS_MERCHANT_ID,
                'token': settings.NETS_TOKEN,
                'operation': 'SALE',
                'transactionId': request.session['enrollment']['transaction_id']
            })
            response = r.text.encode('utf-8')

            dom = etree.fromstring(response)
            response_code = dom.find(".//ResponseCode")
            response_text = dom.find(".//ResponseText")
            payment_verified = False

            if response_code is None:
                # Crap, we didn't get the expected response from Nets.
                # This has happened a few times before. We'll have to handle it ourselves.
                logger.error(u"Mangler 'ResponseCode' element fra Nets",
                    exc_info=sys.exc_info(),
                    extra={
                        'request': request,
                        'nets_response': response,
                        'transaction_id': request.session['enrollment']['transaction_id']
                    }
                )
                request.session['enrollment']['state'] = 'payment'
                return render(request, 'main/enrollment/payment-process-error.html')
            elif response_code.text == '99' and response_text is not None and response_text.text == 'Transaction already processed':
                # The transaction might have already been processed if the user resends the process_card
                # request - recheck nets with a Query request and verify those details
                sale_response = response
                r = requests.get(settings.NETS_QUERY_URL, params={
                    'merchantId': settings.NETS_MERCHANT_ID,
                    'token': settings.NETS_TOKEN,
                    'transactionId': request.session['enrollment']['transaction_id']
                })
                response = r.text.encode('utf-8')
                dom = etree.fromstring(response)
                order_amount = int(dom.find(".//OrderInformation/Amount").text)
                captured_amount = int(dom.find(".//Summary/AmountCaptured").text)
                credited_amount = int(dom.find(".//Summary/AmountCredited").text)

                if order_amount == (captured_amount - credited_amount) == request.session['enrollment']['price_sum'] * 100:
                    payment_verified = True

                logger.warning(u"Transaction already processed - sjekker Query istedet",
                    exc_info=sys.exc_info(),
                    extra={
                        'request': request,
                        'nets_sale_response': sale_response,
                        'nets_query_response': response,
                        'transaction_id': request.session['enrollment']['transaction_id'],
                        'payment_verified': payment_verified,
                        'order_amount': order_amount,
                        'captured_amount': captured_amount,
                        'credited_amount': credited_amount,
                        'price_sum_100': request.session['enrollment']['price_sum'] * 100
                    }
                )

            elif response_code.text == 'OK':
                payment_verified = True

            if payment_verified:
                # Register the payment in focus
                for user in request.session['enrollment']['users']:
                    focus_user = Enrollment.objects.get(memberid=user['id'])
                    focus_user.paid = True
                    focus_user.save()
                prepare_and_send_email(
                    request,
                    request.session['enrollment']['users'],
                    request.session['enrollment']['association'],
                    request.session['enrollment']['location'],
                    'card',
                    request.session['enrollment']['price_sum'])
                request.session['enrollment']['result'] = 'success_card'
            else:
                request.session['enrollment']['result'] = 'fail'
        except requests.ConnectionError as e:
            logger.error(u"(Håndtert, men bør sjekkes) %s" % e.message,
                exc_info=sys.exc_info(),
                extra={'request': request}
            )
            request.session['enrollment']['state'] = 'payment'
            return render(request, 'main/enrollment/payment-process-error.html')

    else:
        request.session['enrollment']['state'] = 'registration'
        request.session['enrollment']['result'] = 'cancel'
    return redirect('enrollment.views.result')

def result(request):
    request.session.modified = True
    if not 'enrollment' in request.session:
        return redirect('enrollment.views.registration')

    if request.session['enrollment']['state'] == 'registration' and request.session['enrollment'].get('result') != 'cancel':
        # Whoops, how did we get here without going through payment first? Redirect back.
        return redirect('enrollment.views.payment_method')
    elif request.session['enrollment']['state'] == 'payment':
        # Not done with payments, why is the user here? Redirect back to payment processing
        if request.session['enrollment']['payment_method'] == 'invoice':
            return redirect('enrollment.views.process_invoice')
        elif request.session['enrollment']['payment_method'] == 'card':
            return redirect("%s?merchantId=%s&transactionId=%s" % (
                settings.NETS_TERMINAL_URL, settings.NETS_MERCHANT_ID, request.session['enrollment']['transaction_id']
            ))

    # Collect emails to a separate list for easier template formatting
    emails = [user['email'] for user in request.session['enrollment']['users'] if user['email'] != '']

    today = date.today()
    new_membership_year = current_membership_year_start()

    skip_header = request.session['enrollment']['result'] == 'success_invoice' or request.session['enrollment']['result'] == 'success_card'
    proof_validity_end = datetime.now() + timedelta(days=TEMPORARY_PROOF_VALIDITY)
    context = {
        'users': request.session['enrollment']['users'],
        'skip_header': skip_header,
        'association': request.session['enrollment']['association'],
        'proof_validity_end': proof_validity_end,
        'emails': emails,
        'location': request.session['enrollment']['location'],
        'price_sum': request.session['enrollment']['price_sum'],
        'today': today,
        'new_membership_year': new_membership_year
    }
    return render(request, 'main/enrollment/result/%s.html' % request.session['enrollment']['result'], context)

def sms(request):
    if not request.is_ajax():
        return redirect('enrollment.views.result')

    if request.method == 'GET':
        # This shouldn't happen, but already did happen twice (according to error logs).
        # We're setting type: POST with ajaxSetup in common.js, so I really have no idea why
        # we sometimes receive GET requests, but since it is reoccuring AND I can't recreate
        # it locally, just account for it so the user actually gets their SMS.
        logger.warning(u"Fikk GET-request på innmeldings-SMS, forventet POST",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        index = int(request.GET['index'])
    else:
        index = int(request.POST['index'])

    # Verify that this is a valid SMS request
    if request.session['enrollment']['state'] != 'complete':
        return HttpResponse(json.dumps({'error': 'enrollment_uncompleted'}))
    if request.session['enrollment']['location']['country'] != 'NO':
        return HttpResponse(json.dumps({'error': 'foreign_number'}))
    if 'sms_sent' in request.session['enrollment']['users'][index]:
        return HttpResponse(json.dumps({'error': 'already_sent'}))
    number = request.session['enrollment']['users'][index]['phone']

    # Render the SMS template
    today = date.today()
    year = today.year
    next_year = today >= current_membership_year_start()
    context = Context({
        'year': year,
        'next_year': next_year,
        'users': request.session['enrollment']['users']
    })
    sms_message = render_to_string('main/enrollment/result/sms.txt', context).encode('utf-8')

    # Send the message
    try:
        r = requests.get(settings.SMS_URL % (quote_plus(number), quote_plus(sms_message)))
        if r.text.find("1 SMS messages added to queue") == -1:
            logger.error(u"Klarte ikke sende SMS-kvittering for innmelding: Ukjent status",
                exc_info=sys.exc_info(),
                extra={
                    'request': request,
                    'response_text': r.text,
                    'sms_request_object': r
                }
            )
            return HttpResponse(json.dumps({'error': 'service_fail'}))
        request.session['enrollment']['users'][index]['sms_sent'] = True
        request.session.modified = True
        return HttpResponse(json.dumps({'error': 'none'}))
    except requests.ConnectionError:
        logger.error(u"Klarte ikke sende SMS-kvittering for innmelding: requests.ConnectionError",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        return HttpResponse(json.dumps({'error': 'connection_error'}))

def prepare_and_send_email(request, users, association, location, payment_method, price_sum):
    email_recipients = [u['email'] for u in users if u['email'] != '']
    if len(users) == 1:
        subject = EMAIL_SUBJECT_SINGLE
        template = 'email-%s-single.html' % payment_method
    else:
        subject = EMAIL_SUBJECT_MULTIPLE
        template = 'email-%s-multiple.html' % payment_method
    # proof_validity_end is not needed for the 'card' payment_method, but ignore that
    proof_validity_end = datetime.now() + timedelta(days=TEMPORARY_PROOF_VALIDITY)
    context = Context({
        'users': users,
        'association': association,
        'location': location,
        'proof_validity_end': proof_validity_end,
        'price_sum': price_sum
    })
    message = render_to_string('main/enrollment/result/%s' % template, context)
    try:
        send_mail(subject, message, EMAIL_FROM, email_recipients)
    except SMTPException:
        # Silently log and ignore this error. The user will have to do without email receipt.
        logger.warning(u"Klarte ikke å sende innmeldingskvitteringepost",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )

def updateIndices(session):
    i = 0
    for user in session['enrollment']['users']:
        user['index'] = i
        i += 1

def validate(request, require_location, require_existing):
    if not 'enrollment' in request.session:
        return redirect("enrollment.views.registration")
    if len(request.session['enrollment']['users']) == 0:
        return redirect("enrollment.views.registration")
    if not validate_youth_count(request.session['enrollment']['users']):
        messages.error(request, 'too_many_underage')
        return redirect("enrollment.views.registration")
    if not validate_user_contact(request.session['enrollment']['users']):
        messages.error(request, 'contact_missing')
        return redirect("enrollment.views.registration")
    if require_location:
        if not 'location' in request.session['enrollment'] or not validate_location(request.session['enrollment']['location']):
            return redirect("%s?%s" % (reverse("enrollment.views.household"), invalid_location))
    if require_existing:
        if request.session['enrollment']['existing'] != '' and not validate_existing(request.session['enrollment']['existing'], request.session['enrollment']['location']['zipcode'], request.session['enrollment']['location']['country']):
            return redirect("%s?%s" % (reverse("enrollment.views.household"), invalid_existing))

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
        # No area provided
        if location['area'].strip() == '':
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
        actor = Actor.objects.get(memberid=id)
    except (Actor.DoesNotExist, ValueError):
        return False

    if datetime.now().year - actor.birth_date.year < AGE_YOUTH:
        return False

    if actor.is_household_member():
        return False

    if actor.get_clean_address().country.code != country:
        return False

    if country == 'NO' and actor.get_clean_address().zipcode.zipcode != zipcode:
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
    if household and age >= AGE_YOUTH:
        return get_membership_type_by_codename('household')['name']
    elif age >= AGE_SENIOR:
        return get_membership_type_by_codename('senior')['name']
    elif age >= AGE_MAIN:
        return get_membership_type_by_codename('main')['name']
    elif age >= AGE_YOUTH:
        return get_membership_type_by_codename('youth')['name']
    elif age >= AGE_SCHOOL:
        return get_membership_type_by_codename('school')['name']
    else:
        return get_membership_type_by_codename('child')['name']

def polite_title(str):
    # If the string is all lowercase or uppercase, apply titling for it
    # Else, assume that the specified case is intentional
    if str.islower() or str.isupper():
        return str.title()
    else:
        return str

def add_focus_user(name, dob, age, gender, location, phone, email, can_have_yearbook, wants_yearbook, linked_to, payment_method, price):
    first_name, last_name = name.rsplit(' ', 1)
    gender = 'M' if gender == 'm' else 'K'
    language = 'nb_no'
    type = focus_type_of(age, linked_to is not None)
    payment_method = FOCUS_PAYMENT_METHOD_CODES[payment_method]
    price = price_of(age, linked_to is not None, price)
    linked_to = '' if linked_to is None else str(linked_to)
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
        area = location['area']
    elif location['country'] == 'DK' or location['country'] == 'SE':
        adr2 = ''
        adr3 = "%s-%s %s" % (location['country'], location['zipcode'], location['area'])
        zipcode = '0000'
        area = ''
    else:
        adr2 = location['address2']
        adr3 = location['address3']
        zipcode = '0000'
        area = ''

    # Fetch and increment memberid with stored procedure
    with transaction.commit_manually():
        cursor = connections['focus'].cursor()
        cursor.execute("exec sp_custTurist_updateMemberId")
        memberid = cursor.fetchone()[0]
        connections['focus'].commit_unless_managed()

    user = Enrollment(
        memberid=memberid,
        last_name=last_name,
        first_name=first_name,
        dob=dob,
        gender=gender,
        linked_to=linked_to,
        adr1=adr1,
        adr2=adr2,
        adr3=adr3,
        country=location['country'],
        phone='',
        email=email,
        receive_yearbook=yearbook,
        type=type,
        yearbook=yearbook_type,
        payment_method=payment_method,
        mob=phone,
        postnr=zipcode,
        poststed=area,
        language=language,
        totalprice=price
    )
    user.save()
    return memberid

def focus_type_of(age, household):
    if household and age >= AGE_YOUTH:
        return get_membership_type_by_codename('household')['code']
    elif age >= AGE_SENIOR:
        return get_membership_type_by_codename('senior')['code']
    elif age >= AGE_MAIN:
        return get_membership_type_by_codename('main')['code']
    elif age >= AGE_YOUTH:
        return get_membership_type_by_codename('youth')['code']
    elif age >= AGE_SCHOOL:
        return get_membership_type_by_codename('school')['code']
    else:
        return get_membership_type_by_codename('child')['code']

def focus_receive_yearbook(age, linked_to):
    if linked_to != '':
        return False
    elif age >= AGE_YOUTH:
        return True
    else:
        return False
