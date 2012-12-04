from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from user.models import Profile
from core import validator
from focus.models import Actor

from user.util import username

def home(request):
    return HttpResponseRedirect('https://%s/minside/' % settings.OLD_SITE)

@login_required
def home_new(request):
    return render(request, 'common/user/home.html')

@login_required
def account(request):
    return render(request, 'common/user/account/account.html')

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

            if User.objects.filter(email=request.POST['email']).exclude(id=request.user.id).exists():
                messages.error(request, 'duplicate_email_address')
                errors = True

            if not errors:
                split = request.POST['name'].split(' ')
                first_name = split[0]
                last_name = ' '.join(split[1:])
                request.user.username = username(request.POST['email'])
                request.user.email = request.POST['email']
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.save()
                messages.info(request, 'update_success')
                return HttpResponseRedirect(reverse('user.views.account'))
            else:
                return HttpResponseRedirect(reverse('user.views.update_account'))
    else:
        if request.method == 'GET':
            context = {
                'user_password_length': settings.USER_PASSWORD_LENGTH
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

            if User.objects.filter(email=request.POST['email']).exclude(id=request.user.id).exists():
                messages.error(request, 'duplicate_email_address')
                errors = True

            if not errors:
                split = request.POST['name'].split(' ')
                first_name = split[0]
                last_name = ' '.join(split[1:])
                request.user.username = username(request.POST['email'])
                request.user.email = request.POST['email']
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.save()
                messages.info(request, 'update_success')
                return HttpResponseRedirect(reverse('user.views.account'))
            else:
                return HttpResponseRedirect(reverse('user.views.update_account'))

@login_required
def update_account_password(request):
    if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
        messages.error(request, 'password_too_short')
        return HttpResponseRedirect(reverse('user.views.update_account'))
    else:
        request.user.set_password(request.POST['password'])
        request.user.save()
        messages.info(request, 'password_update_success')
        return HttpResponseRedirect(reverse('user.views.account'))

@login_required
def become_member(request):
    if request.user.get_profile().memberid is not None:
        return HttpResponseRedirect(reverse('user.views.home_new'))

    if request.method == 'GET':
        return render(request, 'common/user/account/become_member.html')
    else:
        try:
            # Check that the memberid is correct (and retrieve the Actor-entry)
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
                    return HttpResponseRedirect(reverse('user.views.become_member'))
                chosen_email = request.POST['email']
            else:
                raise Exception("Missing email-equal / email-choise-parameters")

            # Check that the user doesn't already have an account
            if Profile.objects.filter(memberid=request.POST['memberid']).exists():
                messages.error(request, 'profile_exists')
                return HttpResponseRedirect(reverse('user.views.become_member'))

            # Check that the email address isn't in use
            if User.objects.filter(username=username(chosen_email)).exclude(id=request.user.id).exists():
                # Note! This COULD be a collision based on our username-algorithm (and pigs COULD fly)
                messages.error(request, 'email_exists')
                return HttpResponseRedirect(reverse('user.views.become_member'))

            # Store focus-user and remove sherpa-stored data
            profile = request.user.get_profile()
            profile.memberid = request.POST['memberid']
            profile.save()

            actor.email = chosen_email
            actor.save()

            request.user.username = username(chosen_email)
            request.user.first_name = ''
            request.user.last_name = ''
            request.user.email = ''
            request.user.save()

            return HttpResponseRedirect(reverse('user.views.home_new'))
        except (Actor.DoesNotExist, ValueError):
            messages.error(request, 'invalid_memberid')
            return HttpResponseRedirect(reverse('user.views.become_member'))
