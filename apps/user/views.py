from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from user.models import Profile
from core import validator

from user.util import username

def home(request):
    return HttpResponseRedirect('https://%s/minside/' % settings.OLD_SITE)

@login_required
def home_new(request):
    return render(request, 'common/user/home.html')

@login_required
def account(request):
    return render(request, 'common/user/account.html')

@login_required
def update_account(request):
    if request.method == 'GET':
        context = {
            'password_length': settings.USER_PASSWORD_LENGTH
        }
        return render(request, 'common/user/update_account.html', context)

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
