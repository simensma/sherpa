from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.db.utils import IntegrityError

import re

from user.models import Profile
from user.views import username

def index(request):
    users = User.objects.all().order_by('first_name')
    context = {'users': users}
    return render(request, 'common/admin/users/index.html', context)

def new(request):
    context = {'password_length': settings.USER_PASSWORD_LENGTH}
    if request.method == 'GET':
        return render(request, 'common/admin/users/new.html', context)
    elif request.method == 'POST':
        try:
            if len(request.POST['name']) == 0:
                raise ValueError("No name provided")
            if len(re.findall('.+@.+\..+', request.POST['email'])) == 0:
                raise ValueError("Invalid email address")
            if len(request.POST['password']) < settings.USER_PASSWORD_LENGTH:
                raise ValueError("Password too short (minimum %s)" % settings.USER_PASSWORD_LENGTH)
            split = request.POST['name'].split(' ')
            first_name = split[0]
            last_name = ' '.join(split[1:])
            user = User.objects.create_user(username(request.POST['email']), request.POST['email'], request.POST['password'])
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            profile = Profile(user=user, phone=request.POST['phone'])
            profile.save()
            messages.add_message(request, messages.INFO, 'created_user')
            return HttpResponseRedirect(reverse('admin.users.views.index'))
        except ValueError:
            messages.add_message(request, messages.ERROR, 'value_error')
            return render(request, 'common/admin/users/new.html', context)
        except IntegrityError:
            messages.add_message(request, messages.ERROR, 'integrity_error')
            return render(request, 'common/admin/users/new.html', context)
