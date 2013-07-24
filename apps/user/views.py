# encoding: utf-8
from django.core.urlresolvers import reverse
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
import logging
import sys
import requests
import hashlib

from user.models import User, NorwayBusTicket, NorwayBusTicketOld
from core import validator
from core.util import current_membership_year_start
from core.models import Zipcode, FocusCountry
from focus.models import Actor
from admin.models import Publication
from aktiviteter.models import AktivitetDate

from focus.util import ADDRESS_FIELD_MAX_LENGTH
from user.util import memberid_lookups_exceeded
from sherpa.decorators import user_requires, user_requires_login

logger = logging.getLogger('sherpa')

NORWAY_EMAIL_FROM = 'Den Norske Turistforening <webmaster@turistforeningen.no>'
NORWAY_EMAIL_RECIPIENT = 'NOR-WAY Bussekspress AS <post@nor-way.no>'

@user_requires_login()
def home(request):
    today = date.today()
    context = {
        'year': today.year,
        'next_year': today >= current_membership_year_start(),
    }
    return render(request, 'common/user/account/home.html', context)

@user_requires_login()
def account(request):
    today = date.today()
    context = {
        'year': today.year,
        'next_year': today >= current_membership_year_start()
    }
    return render(request, 'common/user/account/account.html', context)

@user_requires_login()
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

            if request.user.has_perm('user.sherpa') and 'sherpa-email' in request.POST and not validator.email(request.POST['sherpa-email'], req=False):
                messages.error(request, 'invalid_sherpa_email_address')
                errors = True

            if User.objects.filter(identifier=request.POST['email']).exclude(id=request.user.id).exists():
                messages.error(request, 'duplicate_email_address')
                errors = True

            if errors:
                return redirect('user.views.update_account')

            if request.user.has_perm('user.sherpa') and 'sherpa-email' in request.POST:
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

            if request.user.has_perm('user.sherpa') and 'sherpa-email' in request.POST and not validator.email(request.POST['sherpa-email'], req=False):
                messages.error(request, 'invalid_sherpa_email_address')
                errors = True

            if not validator.phone(request.POST['phone_home'], req=False):
                messages.error(request, 'invalid_phone_home')
                errors = True

            if not validator.phone(request.POST['phone_mobile'], req=False):
                messages.error(request, 'invalid_phone_mobile')
                errors = True

            if request.user.get_actor().get_clean_address().country.code == 'NO' and not request.user.get_actor().is_household_member():
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

            if request.user.has_perm('user.sherpa') and 'sherpa-email' in request.POST:
                user = request.user
                user.sherpa_email = request.POST['sherpa-email']
                user.save()

            actor = request.user.get_actor()
            actor.first_name, actor.last_name = request.POST['name'].rsplit(' ', 1)
            actor.email = request.POST['email']
            actor.phone_home = request.POST['phone_home']
            actor.phone_mobile = request.POST['phone_mobile']
            actor.save()

            if actor.get_clean_address().country.code == 'NO' and not actor.is_household_member():
                actor.address.a1 = request.POST['address']
                if 'address2' in request.POST:
                    actor.address.a2 = request.POST['address2']
                if 'address3' in request.POST:
                    actor.address.a3 = request.POST['address3']
                actor.address.zipcode = zipcode.zipcode
                actor.address.area = zipcode.area
                actor.address.save()

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
            if User.objects.filter(memberid=request.POST['memberid'], is_active=True).exists():
                messages.error(request, 'user_exists')
                return redirect('user.views.register_membership')

            # Ok, registration successful, update the user
            user = request.user

            # If this memberid is already an imported inactive member, merge them
            try:
                other_user = User.objects.get(memberid=request.POST['memberid'], is_active=False)
                user.merge_with(other_user) # This will delete the other user
            except User.DoesNotExist:
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
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def partneroffers(request):
    return render(request, 'common/user/account/partneroffers.html')

@user_requires_login()
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def partneroffers_reserve(request):
    actor = request.user.get_actor()
    actor.reserved_against_partneroffers = json.loads(request.POST['reserve'])
    actor.save()
    return HttpResponse()

@user_requires_login()
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def receive_email(request):
    return render(request, 'common/user/account/receive_email.html')

@user_requires_login()
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def receive_email_set(request):
    actor = request.user.get_actor()
    actor.receive_email = not json.loads(request.POST['reserve'])
    actor.save()
    return HttpResponse()

@user_requires_login()
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def aktiviteter(request):
    aktivitet_dates = AktivitetDate.objects.filter(participants=request.user).order_by('-start_date')
    context = {'aktivitet_dates': aktivitet_dates}
    return render(request, 'common/user/aktiviteter.html', context)

@user_requires_login()
def leader_aktivitet_dates(request):
    aktivitet_dates = request.user.leader_aktivitet_dates.order_by('-start_date')
    context = {'aktivitet_dates': aktivitet_dates}
    return render(request, 'common/user/leader_aktivitet_dates.html', context)

@user_requires_login()
def leader_aktivitet_date(request, aktivitet_date):
    aktivitet_date = AktivitetDate.objects.get(id=aktivitet_date, leaders=request.user)
    context = {'aktivitet_date': aktivitet_date}
    return render(request, 'common/user/leader_aktivitet_date.html', context)

@user_requires_login()
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def publications(request):
    accessible_associations = request.user.get_actor().main_association().get_with_children()
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
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def publication(request, publication):
    accessible_associations = request.user.get_actor().main_association().get_with_children()
    publication = Publication.objects.filter(
        # Verify that the user has access to this publication
        Q(association__type='sentral') |
        Q(access='all') |
        Q(association__in=accessible_associations)
    ).get(id=publication)
    context = {'publication': publication}
    return render(request, 'common/user/account/publication.html', context)

@user_requires_login(message='norway_bus_tickets_login_required')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def norway_bus_tickets(request):
    now = datetime.now()

    try:
        new_ticket = NorwayBusTicket.objects.get(user=request.user)
    except NorwayBusTicket.DoesNotExist:
        new_ticket = None

    try:
        old_ticket = NorwayBusTicketOld.objects.get(memberid=request.user.memberid)
    except NorwayBusTicketOld.DoesNotExist:
        old_ticket = None

    context = {
        'now': now,
        'new_ticket': new_ticket,
        'old_ticket': old_ticket
    }
    return render(request, 'common/user/account/norway_bus_tickets.html', context)

@user_requires_login()
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
    except SMTPException:
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
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def fotobok(request):
    return render(request, 'common/user/account/fotobok.html')

@user_requires_login()
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
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
        ('address1', user.get_actor().address.a1 if user.get_actor().address.a1 is not None else '',),
        ('address2', user.get_actor().address.a2 if user.get_actor().address.a2 is not None else '',),
        ('zipcode', user.get_actor().address.zipcode,),
        ('city', user.get_actor().address.area,),
        ('country', user.get_actor().get_clean_address().country.code,),
        ('phonework', '',),
        ('phonehome', user.get_actor().phone_home if user.get_actor().phone_home is not None else '',),
        ('phonemobile', user.get_actor().phone_mobile if user.get_actor().phone_mobile is not None else '',),
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
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_actor().can_reserve_against_publications(), redirect_to='user.views.home')
def reserve_publications(request):
    return render(request, 'common/user/account/reserve_publications.html')

@user_requires_login()
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_actor().can_reserve_against_publications(), redirect_to='user.views.home')
def reserve_fjellogvidde(request):
    actor = request.user.get_actor()
    actor.set_reserved_against_fjellogvidde(json.loads(request.POST['reserve']))
    actor.save()
    return HttpResponse()

@user_requires_login()
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_actor().can_reserve_against_publications(), redirect_to='user.views.home')
def reserve_yearbook(request):
    actor = request.user.get_actor()
    actor.set_reserved_against_yearbook(json.loads(request.POST['reserve']))
    actor.save()
    return HttpResponse()
