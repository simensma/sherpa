from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.context_processors import PermWrapper
from django.contrib import messages
from django.conf import settings
from django.db.utils import IntegrityError
from django.db.models import Q
from django.template import RequestContext, loader

import re

from user.models import Profile
from user.views import username

def index(request):
    context = {'password_length': settings.USER_PASSWORD_LENGTH}
    return render(request, 'common/admin/users/index.html', context)

def new(request):
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
        return HttpResponseRedirect(reverse('admin.users.views.index'))
    except IntegrityError:
        messages.add_message(request, messages.ERROR, 'integrity_error')
        return HttpResponseRedirect(reverse('admin.users.views.index'))

def show(request, user):
    user = User.objects.get(id=user)
    context = {
        'other_user': user,
        'other_user_perms': PermWrapper(user)}
    return render(request, 'common/admin/users/show.html', context)

def search(request):
    # Todo: Search for membernr.
    users = User.objects.filter(
        Q(first_name__icontains=request.POST['q']) |
        Q(last_name__icontains=request.POST['q'])
        ).order_by('first_name')
    t = loader.get_template('common/admin/users/user_results.html')
    c = RequestContext(request, {'users': users})
    return HttpResponse(t.render(c))
