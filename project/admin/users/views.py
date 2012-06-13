from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.db.utils import IntegrityError

from user.models import Profile
from user.views import username

# Get parameters across views
created_user = 'opprettet_bruker'

@login_required
def index(request):
    users = User.objects.all().order_by('first_name')
    context = {'users': users, 'created_user': request.GET.has_key(created_user)}
    return render(request, 'admin/users/index.html', context)

@login_required
def new(request):
    context = {'password_length': settings.USER_PASSWORD_LENGTH}
    if request.method == 'GET':
        return render(request, 'admin/users/new.html', context)
    elif request.method == 'POST':
        try:
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
            return HttpResponseRedirect("%s?%s" % (reverse('admin.users.views.index'), created_user))
        except ValueError:
            context['value_error'] = True
            return render(request, 'admin/users/new.html', context)
        except IntegrityError:
            context['integrity_error'] = True
            return render(request, 'admin/users/new.html', context)
