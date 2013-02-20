from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.auth.context_processors import PermWrapper
from django.conf import settings
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied

from association.models import Association
from user.models import AssociationRole

def index(request):
    context = {'password_length': settings.USER_PASSWORD_LENGTH}
    return render(request, 'common/admin/users/index.html', context)

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
    context = RequestContext(request, {'users': users})
    return HttpResponse(render_to_string('common/admin/users/user_results.html', context))

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
