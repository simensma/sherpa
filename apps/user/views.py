from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Q

from datetime import datetime
import json

from user.models import Profile
from core import validator
from core.models import Zipcode
from focus.models import Actor
from admin.models import Publication

from user.util import username, memberid_lookups_exceeded
from sherpa.decorators import user_requires
from focus.models import MEMBERSHIP_CODE_HOUSEHOLD, MEMBERSHIP_CODE_LIFELONG

def home(request):
    return HttpResponseRedirect('https://%s/minside/' % settings.OLD_SITE)

@login_required
def home_new(request):
    now = datetime.now()
    context = {
        'year': now.year,
        'next_year': now.month >= settings.MEMBERSHIP_YEAR_START
    }
    return render(request, 'common/user/home.html', context)

@login_required
def account(request):
    now = datetime.now()
    context = {
        'year': now.year,
        'next_year': now.month >= settings.MEMBERSHIP_YEAR_START
    }
    return render(request, 'common/user/account/account.html', context)

@login_required
def update_account(request):
    if request.user.get_profile().memberid is None:
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

            if User.objects.filter(username=username(request.POST['email'])).exclude(id=request.user.id).exists():
                messages.error(request, 'duplicate_email_address')
                errors = True

            if errors:
                return HttpResponseRedirect(reverse('user.views.update_account'))

            if request.user.has_perm('user.sherpa') and 'sherpa-email' in request.POST:
                profile = request.user.get_profile()
                profile.sherpa_email = request.POST['sherpa-email']
                profile.save()

            request.user.username = username(request.POST['email'])
            request.user.email = request.POST['email']
            request.user.first_name, request.user.last_name = request.POST['name'].rsplit(' ', 1)
            request.user.save()
            messages.info(request, 'update_success')
            return HttpResponseRedirect(reverse('user.views.account'))
    else:
        if request.method == 'GET':
            return render(request, 'common/user/account/update_account.html')

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

            if request.user.get_profile().get_actor().address.country == 'NO':
                if not validator.address(request.POST['address']):
                    messages.error(request, 'invalid_address')
                    errors = True

                try:
                    zipcode = Zipcode.objects.get(zipcode=request.POST['zipcode'])
                except Zipcode.DoesNotExist:
                    messages.error(request, 'invalid_zipcode')
                    errors = True

            if errors:
                return HttpResponseRedirect(reverse('user.views.update_account'))

            if request.user.has_perm('user.sherpa') and 'sherpa-email' in request.POST:
                profile = request.user.get_profile()
                profile.sherpa_email = request.POST['sherpa-email']
                profile.save()

            actor = request.user.get_profile().get_actor()
            actor.first_name, actor.last_name = request.POST['name'].rsplit(' ', 1)
            actor.email = request.POST['email']
            actor.phone_home = request.POST['phone_home']
            actor.phone_mobile = request.POST['phone_mobile']
            actor.save()

            if actor.address.country == 'NO':
                actor.address.a1 = request.POST['address']
                actor.address.zipcode = zipcode.zipcode
                actor.address.area = zipcode.area
                actor.address.save()

            messages.info(request, 'update_success')
            return HttpResponseRedirect(reverse('user.views.account'))

@login_required
def account_password(request):
    context = {'user_password_length': settings.USER_PASSWORD_LENGTH}
    return render(request, 'common/user/account/update_account_password.html', context)

@login_required
def update_account_password(request):
    if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
        messages.error(request, 'password_too_short')
        return HttpResponseRedirect(reverse('user.views.account_password'))
    else:
        request.user.set_password(request.POST['password'])
        request.user.save()
        messages.info(request, 'password_update_success')
        return HttpResponseRedirect(reverse('user.views.home_new'))

@login_required
def register_membership(request):
    if request.user.get_profile().memberid is not None:
        return HttpResponseRedirect(reverse('user.views.home_new'))

    if request.method == 'GET':
        context = {'memberid_lookups_limit': settings.MEMBERID_LOOKUPS_LIMIT}
        return render(request, 'common/user/account/register_membership.html', context)
    elif request.method == 'POST':
        try:
            # Check that the memberid is correct (and retrieve the Actor-entry)
            if memberid_lookups_exceeded(request.META['REMOTE_ADDR']):
                messages.error(request, 'memberid_lookups_exceeded')
                return HttpResponseRedirect(reverse('user.views.register_membership'))
            actor = Actor.objects.get(memberid=request.POST['memberid'], address__zipcode=request.POST['zipcode'])

            if request.POST['email-equal'] == 'true':
                # Focus-email is empty, or equal to this email, so just use it
                chosen_email = request.user.get_profile().get_email()
            elif request.POST['email-choice'] == 'sherpa':
                chosen_email = request.user.get_profile().get_email()
            elif request.POST['email-choice'] == 'focus':
                chosen_email = actor.email
            elif request.POST['email-choice'] == 'custom':
                # Check that the email address is valid
                if not validator.email(request.POST['email']):
                    messages.error(request, 'invalid_email')
                    return HttpResponseRedirect(reverse('user.views.register_membership'))
                chosen_email = request.POST['email']
            else:
                raise Exception("Missing email-equal / email-choise-parameters")

            # Check that the user doesn't already have an account
            if Profile.objects.filter(memberid=request.POST['memberid']).exists():
                messages.error(request, 'profile_exists')
                return HttpResponseRedirect(reverse('user.views.register_membership'))

            # Store focus-user and remove sherpa-stored data
            profile = request.user.get_profile()
            profile.memberid = request.POST['memberid']
            profile.save()

            actor.email = chosen_email
            actor.save()

            request.user.username = request.POST['memberid']
            request.user.first_name = ''
            request.user.last_name = ''
            request.user.email = ''
            request.user.save()

            return HttpResponseRedirect(reverse('user.views.home_new'))
        except (Actor.DoesNotExist, ValueError):
            messages.error(request, 'invalid_memberid')
            return HttpResponseRedirect(reverse('user.views.register_membership'))

@login_required
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.register_membership')
def partneroffers(request):
    context = {
        'membership_code_household': MEMBERSHIP_CODE_HOUSEHOLD,
        'membership_code_lifelong': MEMBERSHIP_CODE_LIFELONG}
    return render(request, 'common/user/account/partneroffers.html', context)

@login_required
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.register_membership')
def partneroffers_reserve(request):
    actor = request.user.get_profile().get_actor()
    actor.reserved_against_partneroffers = json.loads(request.POST['reserve'])
    actor.save()
    return HttpResponse()

@login_required
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.register_membership')
def publications(request):
    accessible_associations = request.user.get_profile().get_actor().main_association().get_with_children()
    publications_user_central = Publication.objects.filter(association__type='sentral')
    publications_user_accessible = Publication.objects.filter(association__in=accessible_associations)
    publications_other = Publication.objects.exclude(
        Q(association__in=accessible_associations) |
        Q(association__type='sentral')
    ).filter(access='all')
    context = {
        'publications_user': list(publications_user_central) + list(publications_user_accessible),
        'publications_other': publications_other}
    return render(request, 'common/user/publications.html', context)

@login_required
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.register_membership')
def publication(request, publication):
    accessible_associations = request.user.get_profile().get_actor().main_association().get_with_children()
    publication = Publication.objects.filter(
        # Verify that the user has access to this publication
        Q(association__type='sentral') |
        Q(access='all') |
        Q(association__in=accessible_associations)
    ).get(id=publication)
    context = {'publication': publication}
    return render(request, 'common/user/publication.html', context)

@login_required
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.register_membership')
def reserve_publications(request):
    return render(request, 'common/user/account/reserve_publications.html')

@login_required
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_profile().get_actor().membership_type()['code'] != MEMBERSHIP_CODE_HOUSEHOLD, redirect_to='user.views.home_new')
@user_requires(lambda u: u.get_profile().get_actor().membership_type()['code'] != MEMBERSHIP_CODE_LIFELONG, redirect_to='user.views.home_new')
def reserve_fjellogvidde(request):
    actor = request.user.get_profile().get_actor()
    actor.set_reserved_against_fjellogvidde(json.loads(request.POST['reserve']))
    actor.save()
    return HttpResponse()

@login_required
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_profile().get_actor().membership_type()['code'] != MEMBERSHIP_CODE_HOUSEHOLD, redirect_to='user.views.home_new')
@user_requires(lambda u: u.get_profile().get_actor().membership_type()['code'] != MEMBERSHIP_CODE_LIFELONG, redirect_to='user.views.home_new')
def reserve_yearbook(request):
    actor = request.user.get_profile().get_actor()
    actor.set_reserved_against_yearbook(json.loads(request.POST['reserve']))
    actor.save()
    return HttpResponse()
