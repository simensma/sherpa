# encoding: utf-8
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string

from collections import OrderedDict
from datetime import datetime, date
import json
from smtplib import SMTPException
from ssl import SSLError
import logging
import sys
import requests
import hashlib

from user.models import User, NorwayBusTicket
from core import validator
from core.models import Zipcode, FocusCountry
from focus.models import Actor
from admin.models import Publication
from aktiviteter.models import AktivitetDate
from association.models import Association

from focus.util import ADDRESS_FIELD_MAX_LENGTH
from user.util import memberid_lookups_exceeded
from sherpa.decorators import user_requires, user_requires_login

logger = logging.getLogger('sherpa')

NORWAY_EMAIL_FROM = 'Den Norske Turistforening <webmaster@turistforeningen.no>'
NORWAY_EMAIL_RECIPIENT = 'NOR-WAY Bussekspress AS <post@nor-way.no>'

@user_requires_login()
def home(request):
    if request.user.is_pending and request.user.verify_still_pending():
        return render(request, 'common/user/account/home_pending.html')
    else:
        return render(request, 'common/user/account/home.html')

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
def account(request):
    context = {
        'association_count': Association.objects.filter(type='forening').count()
    }
    return render(request, 'common/user/account/account.html', context)

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
def update_account(request):
    if not request.user.is_member():
        if request.method == 'GET':
            context = {
                'user_password_length': settings.USER_PASSWORD_LENGTH
            }
            return render(request, 'common/user/account/update_account_nonmember.html', context)

        elif request.method == 'POST':
            errors = False

            if not validator.name(request.POST['name']):
                messages.error(request, 'no_name_provided')
                errors = True

            if not validator.email(request.POST['email']):
                messages.error(request, 'invalid_email_address')
                errors = True

            if request.user.has_perm('sherpa') and 'sherpa-email' in request.POST and not validator.email(request.POST['sherpa-email'], req=False):
                messages.error(request, 'invalid_sherpa_email_address')
                errors = True

            if User.objects.filter(identifier=request.POST['email']).exclude(id=request.user.id).exists():
                messages.error(request, 'duplicate_email_address')
                errors = True

            if errors:
                return redirect('user.views.update_account')

            if request.user.has_perm('sherpa') and 'sherpa-email' in request.POST:
                user = request.user
                user.sherpa_email = request.POST['sherpa-email']
                user.save()

            request.user.identifier = request.POST['email']
            request.user.email = request.POST['email']
            request.user.first_name, request.user.last_name = request.POST['name'].rsplit(' ', 1)
            request.user.save()
            messages.info(request, 'update_success')
            return redirect('user.views.account')
    else:
        if request.method == 'GET':
            context = {
                'address_field_max_length': ADDRESS_FIELD_MAX_LENGTH
            }
            return render(request, 'common/user/account/update_account.html', context)

        elif request.method == 'POST':
            errors = False

            if not validator.name(request.POST['name']):
                messages.error(request, 'no_name_provided')
                errors = True

            if not validator.email(request.POST['email']):
                messages.error(request, 'invalid_email_address')
                errors = True

            if request.user.has_perm('sherpa') and 'sherpa-email' in request.POST and not validator.email(request.POST['sherpa-email'], req=False):
                messages.error(request, 'invalid_sherpa_email_address')
                errors = True

            if not validator.phone(request.POST['phone_home'], req=False):
                messages.error(request, 'invalid_phone_home')
                errors = True

            if not validator.phone(request.POST['phone_mobile'], req=False):
                messages.error(request, 'invalid_phone_mobile')
                errors = True

            if request.user.get_address().country.code == 'NO' and not request.user.is_household_member():
                if not validator.address(request.POST['address']):
                    messages.error(request, 'invalid_address')
                    errors = True

                if len(request.POST['address']) >= ADDRESS_FIELD_MAX_LENGTH:
                    messages.error(request, 'too_long_address')
                    errors = True

                try:
                    zipcode = Zipcode.objects.get(zipcode=request.POST['zipcode'])
                except Zipcode.DoesNotExist:
                    messages.error(request, 'invalid_zipcode')
                    errors = True

            if errors:
                return redirect('user.views.update_account')

            if request.user.has_perm('sherpa') and 'sherpa-email' in request.POST:
                user = request.user
                user.sherpa_email = request.POST['sherpa-email']
                user.save()

            first_name, last_name = request.POST['name'].rsplit(' ', 1)
            attributes = {
                'first_name': first_name,
                'last_name': last_name,
                'email': request.POST['email'],
                'phone_home': request.POST['phone_home'],
                'phone_mobile': request.POST['phone_mobile']
            }
            address_attributes = None
            if request.user.get_address().country.code == 'NO' and not request.user.is_household_member():
                address_attributes = {}
                address_attributes['a1'] = request.POST['address']
                if 'address2' in request.POST:
                    address_attributes['a2'] = request.POST['address2']
                if 'address3' in request.POST:
                    address_attributes['a3'] = request.POST['address3']
                address_attributes['zipcode'] = zipcode.zipcode
                address_attributes['area'] = zipcode.area
            request.user.update_personal_data(attributes, address_attributes)

            messages.info(request, 'update_success')
            return redirect('user.views.account')

@user_requires_login()
def account_password(request):
    context = {'user_password_length': settings.USER_PASSWORD_LENGTH}
    return render(request, 'common/user/account/update_account_password.html', context)

@user_requires_login()
def update_account_password(request):
    if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
        messages.error(request, 'password_too_short')
        return redirect('user.views.account_password')
    else:
        request.user.set_password(request.POST['password'])
        request.user.save()
        messages.info(request, 'password_update_success')
        return redirect('user.views.home')

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
def register_membership(request):
    if request.user.is_member():
        return redirect('user.views.home')

    if request.method == 'GET':
        context = {
            'memberid_lookups_limit': settings.MEMBERID_LOOKUPS_LIMIT,
            'countries': FocusCountry.get_sorted()
        }
        return render(request, 'common/user/account/register_membership.html', context)
    elif request.method == 'POST':
        try:
            # Check that the memberid is correct (and retrieve the Actor-entry)
            if memberid_lookups_exceeded(request.META['REMOTE_ADDR']):
                messages.error(request, 'memberid_lookups_exceeded')
                return redirect('user.views.register_membership')
            actor = Actor.objects.get(memberid=request.POST['memberid'], address__zipcode=request.POST['zipcode'])

            if request.POST['email-equal'] == 'true':
                # Focus-email is empty, or equal to this email, so just use it
                chosen_email = request.user.get_email()
            elif request.POST['email-choice'] == 'sherpa':
                chosen_email = request.user.get_email()
            elif request.POST['email-choice'] == 'focus':
                chosen_email = actor.email
            elif request.POST['email-choice'] == 'custom':
                # Check that the email address is valid
                if not validator.email(request.POST['email']):
                    messages.error(request, 'invalid_email')
                    return redirect('user.views.register_membership')
                chosen_email = request.POST['email']
            else:
                raise Exception("Missing email-equal / email-choise-parameters")

            # Check that the user doesn't already have an account
            if User.get_users().filter(memberid=request.POST['memberid'], is_inactive=False).exists():
                messages.error(request, 'user_exists')
                return redirect('user.views.register_membership')

            # Check that the memberid isn't expired.
            # Expired memberids shouldn't exist in Focus, so this is an error and should never happen,
            # but we'll check for it anyway.
            if User.objects.filter(memberid=request.POST['memberid'], is_expired=True).exists():
                messages.error(request, 'expired_user_exists')
                return redirect('user.views.register_membership')

            # Ok, registration successful, update the user
            user = request.user

            try:
                # If this memberid is already an imported inactive member, merge them
                other_user = User.get_users().get(memberid=request.POST['memberid'], is_inactive=True)
                user.merge_with(other_user, move_password=True) # This will delete the other user
            except User.DoesNotExist:
                # It could be a pending user. If inactive, that's fine. If active, they already
                # gave it a password - but they authenticated anyway, so we should still merge them.
                try:
                    other_user = User.objects.get(memberid=request.POST['memberid'], is_pending=True)
                    user.merge_with(other_user, move_password=True) # This will delete the other user
                except User.DoesNotExist:
                    # All right then, the user doesn't exist.
                    pass

            user.memberid = request.POST['memberid']
            user.save()

            # Save the chosen email in Focus
            actor.email = chosen_email
            actor.save()

            # Reset the User-object state, this data will come from Focus
            request.user.identifier = request.POST['memberid']
            request.user.first_name = ''
            request.user.last_name = ''
            request.user.email = ''
            request.user.save()

            return redirect('user.views.home')
        except (Actor.DoesNotExist, ValueError):
            messages.error(request, 'invalid_memberid')
            return redirect('user.views.register_membership')

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def partneroffers(request):
    return render(request, 'common/user/account/partneroffers.html')

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def partneroffers_reserve(request):
    request.user.set_reserved_against_partneroffers(json.loads(request.POST['reserve']))
    return HttpResponse()

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def receive_email(request):
    return render(request, 'common/user/account/receive_email.html')

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def receive_email_set(request):
    request.user.set_receive_email(not json.loads(request.POST['reserve']))
    return HttpResponse()

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def aktiviteter(request):
    aktivitet_dates = AktivitetDate.objects.filter(participants=request.user).order_by('-start_date')
    context = {'aktivitet_dates': aktivitet_dates}
    return render(request, 'common/user/account/aktiviteter.html', context)

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
def turleder_aktivitet_dates(request):
    aktivitet_dates = request.user.turleder_aktivitet_dates.order_by('-start_date')
    context = {'aktivitet_dates': aktivitet_dates}
    return render(request, 'common/user/account/turleder_aktivitet_dates.html', context)

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
def turleder_aktivitet_date(request, aktivitet_date):
    aktivitet_date = AktivitetDate.objects.get(id=aktivitet_date, turledere=request.user)
    context = {'aktivitet_date': aktivitet_date}
    return render(request, 'common/user/account/turleder_aktivitet_date.html', context)

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def publications(request):
    accessible_associations = request.user.main_association().get_with_children()
    publications_user_central = Publication.objects.filter(association__type='sentral')
    publications_user_accessible = Publication.objects.filter(association__in=accessible_associations)
    publications_user = sorted(list(publications_user_central) + list(publications_user_accessible), key=lambda p: p.title)
    publications_other = Publication.objects.exclude(
        Q(association__in=accessible_associations) |
        Q(association__type='sentral')
    ).filter(access='all').order_by('title')
    context = {
        'publications_user': publications_user,
        'publications_other': publications_other
    }
    return render(request, 'common/user/account/publications.html', context)

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def publication(request, publication):
    accessible_associations = request.user.main_association().get_with_children()
    publication = Publication.objects.filter(
        # Verify that the user has access to this publication
        Q(association__type='sentral') |
        Q(access='all') |
        Q(association__in=accessible_associations)
    ).get(id=publication)
    context = {'publication': publication}
    return render(request, 'common/user/account/publication.html', context)

@user_requires_login(message='norway_bus_tickets_login_required')
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def norway_bus_tickets(request):
    now = datetime.now()

    context = {
        'now': now,
    }
    return render(request, 'common/user/account/norway_bus_tickets.html', context)

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.is_eligible_for_norway_bus_tickets(), redirect_to='user.views.home')
def norway_bus_tickets_order(request):
    errors = False

    try:
        travel_date = datetime.strptime(request.POST['date'], "%d.%m.%Y").date()
        today = date.today()
        if travel_date < today or travel_date.year != today.year:
            errors = True
            messages.error(request, 'invalid_date')
    except ValueError:
        errors = True
        messages.error(request, 'invalid_date')

    distance = request.POST['route'].strip()
    if len(distance) == 0:
        errors = True
        messages.error(request, 'missing_distance')

    if errors:
        return redirect('user.views.norway_bus_tickets')

    ticket = NorwayBusTicket(
        user=request.user,
        date_trip=travel_date,
        distance=distance)
    ticket.save()

    try:
        context = RequestContext(request, {'ticket': ticket})
        message = render_to_string('common/user/account/norway_bus_tickets_email.txt', context)
        send_mail(
            "Billettbestilling fra DNT",
            message,
            NORWAY_EMAIL_FROM,
            [NORWAY_EMAIL_RECIPIENT])
        messages.info(request, 'order_success')
        return redirect('user.views.norway_bus_tickets')
    except (SMTPException, SSLError):
        logger.warning(u"Mail til NOR-WAY Bussekspress failet",
            exc_info=sys.exc_info(),
            extra={
                'request': request,
                'user.id': ticket.user.id,
                'date_trip': ticket.date_trip,
                'distance': ticket.distance
            }
        )
        # Delete the erroneous order - yields loss of information, but the above logging
        # should provide the info we need. Otherwise, we'd need a way to mark the order as erroneous.
        ticket.delete()
        messages.error(request, 'email_failure')
        return redirect('user.views.norway_bus_tickets')

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def fotobok(request):
    return render(request, 'common/user/account/fotobok.html')

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.has_paid(), redirect_to='user.views.fotobok')
def fotobok_eurofoto_request(request):
    user = request.user

    # Copied descriptions about the API payload from the old user page fotobok script:
    # publickey  freetext, 36 chars UUID/KEY
    # identifier freetext, 250 chars  <medlemsnummer@eurofoto.turistforeningen.no>
    # firstname  freetext, 250 chars
    # middlename freetext, 250 chars
    # lastname   freetext, 250 chars
    # address1   freetext, 250 chars
    # address2   freetext, 250 chars
    # zipcode    4-10 chars or empty
    # city       freetext, 100 chars
    # country    2 char or empty
    # phonework  8-15 char or empty
    # phonehome  8-15 char or empty
    # phonecell  8-15 char or empty
    # Note: birthdate and gender were commented out and not in use.
    # birthdate  '22.03.1981', dd.mm.yyyy
    # gender     m, f, male, female or blank

    # This needs to be ordered so unpacking it to signature becomes correct
    payload = OrderedDict([
        ('publickey', settings.EUROFOTO_PUBLIC_KEY,),
        ('identifier', '%s@eurofoto.turistforeningen.no' % user.memberid,),
        ('firstname', user.get_first_name(),),
        ('middlename', '',), # We could parse this out of 'lastname', but the old API didn't do that, so whatever
        ('lastname', user.get_last_name(),),
        ('address1', user.get_address().field1,),
        ('address2', user.get_address().field2,),
        ('zipcode', user.get_address().zipcode.zipcode,),
        ('city', user.get_address().zipcode.area,),
        ('country', user.get_address().country.code,),
        ('phonework', '',),
        ('phonehome', user.get_phone_home(),),
        ('phonemobile', user.get_phone_mobile(),),
    ])
    sha1 = hashlib.sha1()
    sha1.update(('%s%s' % (settings.EUROFOTO_PRIVATE_KEY, u''.join(payload.values()).encode('utf-8'))))
    payload['signature'] = sha1.hexdigest()

    try:
        r = requests.post(settings.EUROFOTO_SIGNUP_SERVICE, data=payload)
        reply = json.loads(r.text)
        if reply['result'] and reply['message'] == 'OK':
            return redirect(reply['url'])
        else:
            logger.error(u"Ukjent svar fra Eurofoto-API",
                exc_info=sys.exc_info(),
                extra={
                    'request': request,
                    'reply': reply
                }
            )
            messages.error(request, 'eurofoto_api_unparseable_reply')
            return redirect('user.views.fotobok')
    except requests.ConnectionError as e:
        logger.warning(e.message,
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        messages.error(request, 'eurofoto_api_connection_error')
        return redirect('user.views.fotobok')
    except ValueError as e:
        logger.error(e.message,
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        messages.error(request, 'eurofoto_api_unparseable_reply')
        return redirect('user.views.fotobok')

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.can_reserve_against_publications(), redirect_to='user.views.home')
def reserve_publications(request):
    return render(request, 'common/user/account/reserve_publications.html')

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.can_reserve_against_publications(), redirect_to='user.views.home')
def reserve_fjellogvidde(request):
    request.user.set_reserved_against_fjellogvidde(json.loads(request.POST['reserve']))
    return HttpResponse()

@user_requires_login()
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.can_reserve_against_publications(), redirect_to='user.views.home')
def reserve_yearbook(request):
    request.user.set_reserved_against_yearbook(json.loads(request.POST['reserve']))
    return HttpResponse()
