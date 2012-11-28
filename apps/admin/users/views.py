from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.auth.context_processors import PermWrapper
from django.contrib import messages
from django.conf import settings
from django.db.utils import IntegrityError
from django.db.models import Q
from django.template import RequestContext, loader
from django.core.exceptions import PermissionDenied

import re

from association.models import Association
from user.models import Profile, AssociationRole
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
        return HttpResponseRedirect(reverse('admin.users.views.show', args=[user.id]))
    except ValueError:
        messages.error(request, 'value_error')
        return HttpResponseRedirect(reverse('admin.users.views.index'))
    except IntegrityError:
        messages.error(request, 'integrity_error')
        return HttpResponseRedirect(reverse('admin.users.views.index'))

def show(request, user):
    user = User.objects.get(id=user)

    # Admins can assign user/admin, users can assign users
    assignable_admin = request.user.get_profile().all_associations('admin')
    assignable_user = request.user.get_profile().all_associations('user').exclude(associationrole__profile=user.get_profile())
    assignable_associations = assignable_admin | assignable_user

    # Only admins can revoke association relation
    revokable_associations = user.get_profile().all_associations() & request.user.get_profile().all_associations('admin')

    context = {
        'other_user': user,
        'other_user_perms': PermWrapper(user),
        'other_user_associations': Association.sort_and_apply_roles(user.get_profile().all_associations(), user),
        'revokable_associations': Association.sort(revokable_associations),
        'assignable_associations': Association.sort_and_apply_roles(assignable_associations, request.user)}
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

def give_sherpa_access(request, user):
    if not request.user.has_perm('user.sherpa'):
        raise PermissionDenied

    permission = Permission.objects.get(content_type__app_label='user', codename='sherpa')
    User.objects.get(id=user).user_permissions.add(permission)
    return HttpResponseRedirect(reverse('admin.users.views.show', args=[user]))

def revoke_sherpa_access(request, user):
    if not request.user.has_perm('user.sherpa'):
        raise PermissionDenied

    permission = Permission.objects.get(content_type__app_label='user', codename='sherpa')
    User.objects.get(id=user).user_permissions.remove(permission)
    return HttpResponseRedirect(reverse('admin.users.views.show', args=[user]))

def make_sherpa_admin(request, user):
    if not request.user.has_perm('user.sherpa_admin'):
        raise PermissionDenied

    permission = Permission.objects.get(content_type__app_label='user', codename='sherpa_admin')
    User.objects.get(id=user).user_permissions.add(permission)
    return HttpResponseRedirect(reverse('admin.users.views.show', args=[user]))

def add_association_permission(request):
    user = User.objects.get(id=request.POST['user'])
    association = Association.objects.get(id=request.POST['association'])

    role_valid = False
    for role in AssociationRole.ROLE_CHOICES:
        if role[0] == request.POST['role']:
            role_valid = True
            break
    if not role_valid:
        raise PermissionDenied

    # Verify that the user performing this action has the required permissions
    if not request.user.has_perm('user.sherpa_admin'):
        try:
            role = AssociationRole.objects.get(profile=request.user.get_profile(), association=association)
            if role.role == 'user' and request.POST['role'] == 'admin':
                raise PermissionDenied
        except AssociationRole.DoesNotExist:
            raise PermissionDenied

    try:
        role = AssociationRole.objects.get(profile=user.get_profile(), association=association)
        role.role = request.POST['role']
        role.save()
    except AssociationRole.DoesNotExist:
        role = AssociationRole(profile=user.get_profile(), association=association, role=request.POST['role'])
        role.save()

    return HttpResponseRedirect(reverse('admin.users.views.show', args=[user.id]))

def revoke_association_permission(request):
    user = User.objects.get(id=request.POST['user'])
    association = Association.objects.get(id=request.POST['association'])

    # Verify that the user performing this action has the required permissions
    if not request.user.has_perm('user.sherpa_admin'):
        try:
            if AssociationRole.objects.get(profile=request.user.get_profile(), association=association).role != 'admin':
                raise PermissionDenied
        except AssociationRole.DoesNotExist:
            raise PermissionDenied

    role = AssociationRole.objects.get(profile=user.get_profile(), association=association)
    role.delete()
    return HttpResponseRedirect(reverse('admin.users.views.show', args=[user.id]))
