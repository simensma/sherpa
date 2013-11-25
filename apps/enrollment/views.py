# encoding: utf-8
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.cache import cache
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from core.models import Zipcode, FocusCountry
from sherpa2.models import Association
from focus.models import FocusZipcode, Enrollment as FocusEnrollment, Actor, ActorAddress
from focus.util import get_membership_type_by_codename
from enrollment.models import State, User as EnrollmentUser, Transaction
from enrollment.util import current_template_layout, get_or_create_enrollment, prepare_and_send_email, polite_title, TEMPORARY_PROOF_VALIDITY, KEY_PRICE, FOREIGN_SHIPMENT_PRICE, invalid_location, invalid_existing, AGE_SENIOR, AGE_MAIN, AGE_YOUTH, AGE_SCHOOL
from enrollment.validation import validate, validate_location
from user.models import User
from association.models import DNT_OSLO_ID

from datetime import datetime, timedelta
import requests
import re
import json
import logging
import sys
from lxml import etree
from urllib import quote_plus

logger = logging.getLogger('sherpa')

# Registration states: 'registration' -> 'payment' -> 'complete'
# These are used in most views to know where the user came from and where
# they should be headed.

def index(request):
    return redirect("enrollment.views.registration")

def registration(request, user):
    enrollment = get_or_create_enrollment(request)

    if enrollment.state == 'payment':
        # Payment has been initiated but the user goes back to the registration page - why?
        # Maybe it failed, and they want to retry registration?
        # Reset the state and let them reinitiate payment when they're ready.
        enrollment.state = 'registration'
        enrollment.save()
    elif enrollment.state == 'complete':
        # A previous registration has been completed, but a new one has been initiated.
        # Remove the old one and start over.
        del request.session['enrollment']
        enrollment = get_or_create_enrollment(request)

    # User set via URL means a GET request to view some user
    if user is not None:
        try:
            user = enrollment.users.all().get(id=user)
        except EnrollmentUser.DoesNotExist:
            return redirect('enrollment.views.registration')

    errors = False
    if request.method == 'POST':

        # This is a POST, if editing an existing user it will be set via the form
        if 'user' in request.POST:
            user = enrollment.users.all().get(id=request.POST['user'])
        else:
            user = EnrollmentUser(enrollment=enrollment)

        try:
            dob = datetime.strptime(request.POST['dob'], "%d.%m.%Y")
        except ValueError:
            dob = None

        # Titleize and strip whitespace before/after dash
        user.name = re.sub('\s*-\s*', '-', polite_title(request.POST['name'].strip()))
        user.phone = request.POST['phone'].strip()
        user.email = request.POST['email'].lower().strip()
        user.gender = request.POST.get('gender', '')
        user.key = request.POST.get('key') == 'on'
        user.dob = dob
        user.save()

        if user.is_valid():
            enrollment.users.add(user)
            # The user was saved successfully, so clear the form for the next user
            user = None
        else:
            errors = True

    if not errors and 'forward' in request.POST:
        return redirect("enrollment.views.household")

    context = {
        'enrollment': enrollment,
        'current_user': user,
        'errors': errors,
    }
    context.update(current_template_layout(request))
    return render(request, 'main/enrollment/registration.html', context)

def remove(request, user):
    enrollment = get_or_create_enrollment(request)

    try:
        enrollment.users.get(id=user).delete()
    except EnrollmentUser.DoesNotExist:
        # Ignore it and redirect the user back. Maybe they tried to URL-hack or something.
        pass

    return redirect("enrollment.views.registration")

def household(request):
    enrollment = get_or_create_enrollment(request)

    # Since conditions is checked client-side, they must've accepted them if they reach this point.
    enrollment.accepts_conditions = True
    enrollment.save()

    validation = validate(enrollment, require_location=False, require_existing=False)
    if not validation['valid']:
        if 'message' in validation:
            messages.error(request, validation['message'])
        return redirect(validation['redirect'])

    if enrollment.state == 'payment':
        # Payment has been initiated but the user goes back here - why?
        # Reset the state and let them reinitiate payment when they're ready.
        enrollment.state = 'registration'
        enrollment.save()
    elif enrollment.state == 'complete':
        # A previous registration has been completed, so why would the user come directly here?
        # Just redirect them back to registration which will restart a new registration.
        return redirect("enrollment.views.registration")

    errors = invalid_location in request.GET
    if request.method == 'POST':
        enrollment.country = request.POST['country']
        enrollment.address1 = polite_title(request.POST['address1'])
        enrollment.address2 = polite_title(request.POST['address2'])
        enrollment.address3 = polite_title(request.POST['address3'])
        enrollment.zipcode = request.POST['zipcode']
        enrollment.area = request.POST.get('area', '')
        enrollment.existing_memberid = request.POST['existing']
        enrollment.wants_yearbook = enrollment.country != 'NO' and 'yearbook' in request.POST
        enrollment.attempted_yearbook = False
        if enrollment.wants_yearbook:
            if enrollment.existing_memberid != '' or not enrollment.has_potential_main_member():
                enrollment.wants_yearbook = False
                enrollment.attempted_yearbook = True
        enrollment.save()

        if validate_location(enrollment):
            if enrollment.country != 'NO':
                return redirect('enrollment.views.verification')
            else:
                try:
                    focus_zipcode = FocusZipcode.objects.get(zipcode=enrollment.zipcode)
                    Association.objects.get(focus_id=focus_zipcode.main_association_id) # Verify that the Association exists
                    return redirect('enrollment.views.verification')
                except FocusZipcode.DoesNotExist:
                    # We know that this zipcode exists in Zipcode, because validate_location validated, and it checks for that
                    logger.warning(u"Postnummer finnes i Zipcode, men ikke i Focus!",
                        exc_info=sys.exc_info(),
                        extra={
                            'request': request,
                            'postnummer': enrollment.zipcode
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

    context = {
        'enrollment': enrollment,
        'invalid_existing': invalid_existing in request.GET,
        'countries': FocusCountry.get_sorted(),
        'foreign_shipment_price': FOREIGN_SHIPMENT_PRICE,
        'errors': errors,
    }
    context.update(current_template_layout(request))
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
    enrollment = get_or_create_enrollment(request)

    validation = validate(enrollment, require_location=True, require_existing=True)
    if not validation['valid']:
        if 'message' in validation:
            messages.error(request, validation['message'])
        return redirect(validation['redirect'])

    if enrollment.state == 'payment':
        # Payment has been initiated but the user goes back here - why?
        # Reset the state and let them reinitiate payment when they're ready.
        enrollment.state = 'registration'
        enrollment.save()
    elif enrollment.state == 'complete':
        # A previous registration has been completed, so why would the user come directly here?
        # Just redirect them back to registration which will restart a new registration.
        return redirect("enrollment.views.registration")

    # If existing member is specified, save details and change to that address
    existing_name = ''
    if enrollment.existing_memberid != '':
        actor = Actor.objects.get(memberid=enrollment.existing_memberid)
        existing_name = "%s %s" % (actor.first_name, actor.last_name)
        enrollment.country = actor.get_clean_address().country.code
        if actor.get_clean_address().country.code == 'NO':
            enrollment.address1 = actor.get_clean_address().field1
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
            enrollment.country = actor.get_clean_address().country.code
            enrollment.address1 = actor.get_clean_address().field1
            enrollment.address2 = actor.get_clean_address().field2
            enrollment.address3 = actor.get_clean_address().field3

    # Get the area name for this zipcode
    if enrollment.country == 'NO':
        enrollment.area = Zipcode.objects.get(zipcode=enrollment.zipcode).area

    # Figure out which association this member/these members will belong to
    if enrollment.existing_memberid != '':
        # Use main members' association if applicable
        focus_association_id = Actor.objects.get(memberid=enrollment.existing_memberid).main_association_id
        association = cache.get('association_sherpa2.focus.%s' % focus_association_id)
        if association is None:
            association = Association.objects.get(focus_id=focus_association_id)
            cache.set('association_sherpa2.focus.%s' % focus_association_id, association, 60 * 60 * 24 * 7)
    else:
        if enrollment.country == 'NO':
            focus_association_id = cache.get('focus.zipcode_association.%s' % enrollment.zipcode)
            if focus_association_id is None:
                focus_association_id = FocusZipcode.objects.get(zipcode=enrollment.zipcode).main_association_id
                cache.set('focus.zipcode_association.%s' % enrollment.zipcode, focus_association_id, 60 * 60 * 24 * 7)
            association = cache.get('association_sherpa2.focus.%s' % focus_association_id)
            if association is None:
                association = Association.objects.get(focus_id=focus_association_id)
                cache.set('association_sherpa2.focus.%s' % focus_association_id, association, 60 * 60 * 24 * 7)
        else:
            # Foreign members are registered with DNT Oslo og Omegn
            association = cache.get('association_sherpa2.%s' % DNT_OSLO_ID)
            if association is None:
                association = Association.objects.get(id=DNT_OSLO_ID)
                cache.set('association_sherpa2.%s' % DNT_OSLO_ID, association, 60 * 60 * 24 * 7)
    enrollment.association = association.id
    enrollment.save()

    keycount = 0
    youth_or_older_count = 0
    main = None
    for user in enrollment.users.all():
        if main is None or (user.get_age() < main.get_age() and user.get_age() >= AGE_YOUTH):
            # The cheapest option will be to set the youngest member, 19 or older, as main member
            main = user
        if user.get_age() >= AGE_YOUTH:
            youth_or_older_count += 1
        if user.key:
            keycount += 1
    keyprice = keycount * KEY_PRICE
    multiple_main = youth_or_older_count > 1
    context = {
        'enrollment': enrollment,
        'existing_name': existing_name,
        'keycount': keycount,
        'keyprice': keyprice,
        'multiple_main': multiple_main,
        'main': main,
        'age_senior': AGE_SENIOR,
        'age_main': AGE_MAIN,
        'age_youth': AGE_YOUTH,
        'age_school': AGE_SCHOOL,
        'membership_type_names': {
            'senior': get_membership_type_by_codename('senior')['name'],
            'main': get_membership_type_by_codename('main')['name'],
            'youth': get_membership_type_by_codename('youth')['name'],
            'school': get_membership_type_by_codename('school')['name'],
            'child': get_membership_type_by_codename('child')['name'],
            'household': get_membership_type_by_codename('household')['name'],
        },
        'foreign_shipment_price': FOREIGN_SHIPMENT_PRICE,
    }
    context.update(current_template_layout(request))
    return render(request, 'main/enrollment/verification.html', context)

def payment_method(request):
    enrollment = get_or_create_enrollment(request)

    validation = validate(enrollment, require_location=True, require_existing=True)
    if not validation['valid']:
        if 'message' in validation:
            messages.error(request, validation['message'])
        return redirect(validation['redirect'])

    if enrollment.state == 'payment':
        # Payment has been initiated but the user goes back here - why?
        # Reset the state and let them reinitiate payment when they're ready.
        enrollment.state = 'registration'
        enrollment.save()
    elif enrollment.state == 'complete':
        # A previous registration has been completed, so why would the user come directly here?
        # Just redirect them back to registration which will restart a new registration.
        return redirect("enrollment.views.registration")

    enrollment.users.all().update(chosen_main_member=False)
    if 'main-member' in request.POST and request.POST['main-member'] != '':
        user = enrollment.users.get(id=request.POST['main-member'])

        if not user.can_be_main_member():
            messages.error(request, 'invalid_main_member')
            return redirect('enrollment.views.verification')

        user.chosen_main_member = True
        user.save()
    else:
        # No choice made, in this situation, there should be an existing member specified,
        # only one available main member, or none at all.
        if enrollment.existing_memberid == '':
            main_members = [user for user in enrollment.users.all() if user.can_be_main_member()]
            if len(main_members) == 1:
                main_members[0].chosen_main_member = True
                main_members[0].save()
            elif len(main_members) > 1:
                logger.warning(u"More than one available main members and no choice made. Fix the UI",
                    exc_info=sys.exc_info(),
                    extra={
                        'request': request,
                        'main_members': main_members,
                        'enrollment': enrollment,
                    }
                )
                messages.error(request, 'no_main_member')
                return redirect('enrollment.views.verification')

    context = {
        'card_available': State.objects.all()[0].card,
        'card_required': 'innmelding.aktivitet' in request.session,
    }
    context.update(current_template_layout(request))
    return render(request, 'main/enrollment/payment.html', context)

def payment(request):
    enrollment = get_or_create_enrollment(request)

    validation = validate(enrollment, require_location=True, require_existing=True)
    if not validation['valid']:
        if 'message' in validation:
            messages.error(request, validation['message'])
        return redirect(validation['redirect'])

    # If for some reason the user managed to POST 'card' as payment_method
    if not State.objects.all()[0].card and request.POST.get('payment_method', '') == 'card':
        return redirect('enrollment.views.payment_method')

    # Enrollments through ordering require card payment
    if 'innmelding.aktivitet' in request.session and request.POST.get('payment_method', '') != 'card':
        return redirect('enrollment.views.payment_method')

    if enrollment.state == 'registration':
        # All right, enter payment state
        enrollment.state = 'payment'
        enrollment.save()
    elif enrollment.state == 'payment':
        # Already in payment state, redirect them forwards to processing
        if enrollment.payment_method == 'invoice':
            return redirect('enrollment.views.process_invoice')
        elif enrollment.payment_method == 'card':
            # Let's check for an existing transaction first
            if enrollment.get_active_transaction() is not None:
                # Yeah, it's there. Skip payment and redirect forwards to processing
                return redirect("%s?merchantId=%s&transactionId=%s" % (
                    settings.NETS_TERMINAL_URL, settings.NETS_MERCHANT_ID, enrollment.get_active_transaction().transaction_id
                ))
            else:
                # No active transactions - maybe a problem occured during payment.
                # Assume payment failed and just redo it - if something failed, we'll know
                # through logs and hopefully discover any double-payments
                pass
    elif enrollment.state == 'complete':
        # Registration has already been completed, redirect forwards to results page
        return redirect('enrollment.views.result')

    if request.POST.get('payment_method', '') != 'card' and request.POST.get('payment_method', '') != 'invoice':
        messages.error(request, 'invalid_payment_method')
        return redirect('enrollment.views.payment_method')
    enrollment.payment_method = request.POST['payment_method']
    enrollment.save()

    # Ok, we're good to go. Save all users to Focus
    enrollment.save_users_to_focus()

    # If we're paying by invoice, skip ahead to invoice processing
    if enrollment.payment_method == 'invoice':
        return redirect('enrollment.views.process_invoice')

    # Paying with card, move on.
    order_number = Transaction.generate_order_number()
    main_or_random_member = enrollment.get_main_or_random_member()
    first_name, last_name = main_or_random_member.name.rsplit(' ', 1)

    context = RequestContext(request)
    description = render_to_string('main/enrollment/payment-terminal.html', context)

    # Send the transaction registration to Nets
    try:
        r = requests.get(settings.NETS_REGISTER_URL, params={
            'merchantId': settings.NETS_MERCHANT_ID,
            'token': settings.NETS_TOKEN,
            'orderNumber': order_number,
            'customerFirstName': first_name,
            'customerLastName': last_name,
            'customerEmail': main_or_random_member.email,
            'currencyCode': 'NOK',
            'amount': enrollment.get_total_price() * 100,
            'orderDescription': description,
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
    transaction = Transaction(
        enrollment=enrollment,
        transaction_id=etree.fromstring(response).find("TransactionId").text,
        order_number=order_number,
        state='register'
    )
    transaction.save()

    return redirect("%s?merchantId=%s&transactionId=%s" % (
        settings.NETS_TERMINAL_URL, settings.NETS_MERCHANT_ID, transaction.transaction_id
    ))

def process_invoice(request):
    if not 'enrollment' in request.session:
        return redirect('enrollment.views.registration')
    enrollment = get_or_create_enrollment(request)

    if enrollment.state == 'registration':
        # Whoops, how did we get here without going through payment first? Redirect back.
        return redirect('enrollment.views.payment_method')
    elif enrollment.state == 'payment':
        # Cool, this is where we want to be. Update the state to 'complete'
        enrollment.state = 'complete'
        enrollment.save()
    elif enrollment.state == 'complete':
        # Registration has already been completed, redirect forwards to results page
        return redirect('enrollment.views.result')

    for user in enrollment.users.all():
        user.pending_user = User.create_pending(user.memberid)
        user.save()

    prepare_and_send_email(request, enrollment)
    enrollment.result = 'success_invoice'
    enrollment.save()
    return redirect('enrollment.views.result')

def process_card(request):
    if not 'enrollment' in request.session:
        return redirect('enrollment.views.registration')
    enrollment = get_or_create_enrollment(request)

    if enrollment.state == 'registration':
        # Whoops, how did we get here without going through payment first? Redirect back.
        # Note, *this* makes it impossible to use a previously verified transaction id
        # on a *second* registration by skipping the payment view and going straight to this check.
        return redirect('enrollment.views.payment_method')
    elif enrollment.state == 'payment':
        # Cool, this is where we want to be. Update the state to 'complete'
        enrollment.state = 'complete'
        enrollment.save()
    elif enrollment.state == 'complete':
        # Registration has already been completed, redirect forwards to results page
        return redirect('enrollment.views.result')

    if request.GET['responseCode'] == 'OK':
        try:
            r = requests.get(settings.NETS_PROCESS_URL, params={
                'merchantId': settings.NETS_MERCHANT_ID,
                'token': settings.NETS_TOKEN,
                'operation': 'SALE',
                'transactionId': enrollment.get_active_transaction().transaction_id
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
                        'enrollment': enrollment,
                        'transaction_id': enrollment.get_active_transaction().transaction_id
                    }
                )
                enrollment.state = 'payment'
                enrollment.save()
                context = current_template_layout(request)
                return render(request, 'main/enrollment/payment-process-error.html', context)
            elif response_code.text == '99' and response_text is not None and response_text.text == 'Transaction already processed':
                # The transaction might have already been processed if the user resends the process_card
                # request - recheck nets with a Query request and verify those details
                sale_response = response
                r = requests.get(settings.NETS_QUERY_URL, params={
                    'merchantId': settings.NETS_MERCHANT_ID,
                    'token': settings.NETS_TOKEN,
                    'transactionId': enrollment.get_active_transaction().transaction_id
                })
                response = r.text.encode('utf-8')
                dom = etree.fromstring(response)
                order_amount = int(dom.find(".//OrderInformation/Amount").text)
                captured_amount = int(dom.find(".//Summary/AmountCaptured").text)
                credited_amount = int(dom.find(".//Summary/AmountCredited").text)

                if order_amount == (captured_amount - credited_amount) == enrollment.get_total_price() * 100:
                    payment_verified = True

                logger.warning(u"Transaction already processed - sjekker Query istedet",
                    exc_info=sys.exc_info(),
                    extra={
                        'request': request,
                        'enrollment': enrollment,
                        'nets_sale_response': sale_response,
                        'nets_query_response': response,
                        'transaction_id': enrollment.get_active_transaction().transaction_id,
                        'payment_verified': payment_verified,
                        'order_amount': order_amount,
                        'captured_amount': captured_amount,
                        'credited_amount': credited_amount,
                        'total_price_100': enrollment.get_total_price() * 100
                    }
                )

            elif response_code.text == 'OK':
                payment_verified = True

            if payment_verified:
                # Mark the transaction as successful
                transaction = enrollment.get_active_transaction()
                transaction.state = 'success'
                transaction.save()

                # Register the payment in focus
                for user in enrollment.users.all():
                    focus_user = FocusEnrollment.objects.get(memberid=user.memberid)
                    focus_user.paid = True
                    focus_user.save()
                    user.pending_user = User.create_pending(user.memberid)
                    user.save()
                prepare_and_send_email(request, enrollment)
                enrollment.result = 'success_card'
                enrollment.save()
            else:
                transaction = enrollment.get_active_transaction()
                transaction.state = 'fail'
                transaction.save()

                enrollment.result = 'fail'
                enrollment.state = 'registration'
                enrollment.save()
        except requests.ConnectionError as e:
            logger.error(u"(Håndtert, men bør sjekkes) %s" % e.message,
                exc_info=sys.exc_info(),
                extra={'request': request}
            )
            enrollment.state = 'payment'
            enrollment.save()
            context = current_template_layout(request)
            return render(request, 'main/enrollment/payment-process-error.html', context)

    else:
        transaction = enrollment.get_active_transaction()
        transaction.state = 'cancel'
        transaction.save()

        enrollment.state = 'registration'
        enrollment.result = 'cancel'
        enrollment.save()
    return redirect('enrollment.views.result')

def result(request):
    if not 'enrollment' in request.session:
        return redirect('enrollment.views.registration')
    enrollment = get_or_create_enrollment(request)

    if enrollment.state == 'registration' and enrollment.result not in ['cancel', 'fail']:
        # Whoops, how did we get here without going through payment first? Redirect back.
        return redirect('enrollment.views.payment_method')
    elif enrollment.state == 'payment':
        # Not done with payments, why is the user here? Redirect back to payment processing
        if enrollment.payment_method == 'invoice':
            return redirect('enrollment.views.process_invoice')
        elif enrollment.payment_method == 'card':
            return redirect("%s?merchantId=%s&transactionId=%s" % (
                settings.NETS_TERMINAL_URL, settings.NETS_MERCHANT_ID, enrollment.get_active_transaction().transaction_id
            ))

    # Collect emails to a separate list for easier template formatting
    emails = [user.email for user in enrollment.users.all() if user.email != '']

    skip_header = enrollment.result == 'success_invoice' or enrollment.result == 'success_card'
    proof_validity_end = datetime.now() + timedelta(days=TEMPORARY_PROOF_VALIDITY)
    context = {
        'enrollment': enrollment,
        'skip_header': skip_header,
        'proof_validity_end': proof_validity_end,
        'emails': emails,
        'innmelding_aktivitet': request.session.get('innmelding.aktivitet')
    }
    context.update(current_template_layout(request))
    return render(request, 'main/enrollment/result/%s.html' % enrollment.result, context)

def sms(request):
    if not request.is_ajax():
        return redirect('enrollment.views.result')

    if not 'enrollment' in request.session:
        raise PermissionDenied

    enrollment = get_or_create_enrollment(request)

    if request.method == 'GET':
        # This shouldn't happen, but already did happen twice (according to error logs).
        # We're setting type: POST with ajaxSetup in common.js, so I really have no idea why
        # we sometimes receive GET requests, but since it is reoccuring AND I can't recreate
        # it locally, just account for it so the user actually gets their SMS.
        logger.warning(u"Fikk GET-request på innmeldings-SMS, forventet POST",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        user = int(request.GET['user'])
    else:
        user = int(request.POST['user'])

    user = enrollment.users.get(id=user)

    # Verify that this is a valid SMS request
    if enrollment.state != 'complete':
        return HttpResponse(json.dumps({'error': 'enrollment_uncompleted'}))
    if enrollment.country != 'NO':
        return HttpResponse(json.dumps({'error': 'foreign_number'}))
    if user.sms_sent:
        return HttpResponse(json.dumps({'error': 'already_sent'}))

    # Render the SMS template
    context = RequestContext(request, {
        'users': enrollment.get_users_by_name()
    })
    sms_message = render_to_string('main/enrollment/result/sms.txt', context).encode('utf-8')

    # Send the message
    try:
        r = requests.get(settings.SMS_URL % (quote_plus(user.phone), quote_plus(sms_message)))
        if r.text.find("1 SMS messages added to queue") == -1:
            logger.error(u"Klarte ikke sende SMS-kvittering for innmelding: Ukjent status",
                exc_info=sys.exc_info(),
                extra={
                    'request': request,
                    'enrollment': enrollment,
                    'response_text': r.text,
                    'sms_request_object': r
                }
            )
            return HttpResponse(json.dumps({'error': 'service_fail'}))
        user.sms_sent = True
        user.save()
        return HttpResponse(json.dumps({'error': 'none'}))
    except requests.ConnectionError:
        logger.error(u"Klarte ikke sende SMS-kvittering for innmelding: requests.ConnectionError",
            exc_info=sys.exc_info(),
            extra={
                'request': request,
                'enrollment': enrollment,
            }
        )
        return HttpResponse(json.dumps({'error': 'connection_error'}))
