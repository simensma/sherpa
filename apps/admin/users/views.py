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
from user.models import Profile, AssociationRole
from focus.models import Actor

def index(request):
    context = {'password_length': settings.USER_PASSWORD_LENGTH}
    return render(request, 'common/admin/users/index.html', context)

def show(request, user):
    user = User.objects.get(id=user)

    # Admins can assign user/admin, users can assign users
    assignable_admin = request.user.get_profile().associations_with_role('admin')
    assignable_user = request.user.get_profile().associations_with_role('user').exclude(associationrole__profile=user.get_profile())
    assignable_associations = assignable_admin | assignable_user

    # Only admins can revoke association relation
    revokable_associations = user.get_profile().all_associations() & request.user.get_profile().associations_with_role('admin')

    context = {
        'other_user': user,
        'other_user_perms': PermWrapper(user),
        'revokable_associations': Association.sort(revokable_associations),
        'assignable_associations': Association.sort(assignable_associations)}
    return render(request, 'common/admin/users/show.html', context)

def search(request):
    local_profiles = Profile.objects.all()
    for word in request.POST['q'].split():
        local_profiles = local_profiles.filter(
            Q(user__first_name__icontains=word) |
            Q(user__last_name__icontains=word))
    local_profiles = local_profiles.order_by('user__first_name')

    actors = Actor.objects.all()
    for word in request.POST['q'].split():
        actors = actors.filter(
            Q(first_name__icontains=word) |
            Q(last_name__icontains=word) |
            Q(memberid__icontains=word))
    actors = actors.order_by('first_name')

    members = Profile.objects.filter(memberid__in=list(actors.values_list('memberid', flat=True)))
    actors_wihtout_profile = actors.exclude(memberid__in=list(members.values_list('memberid', flat=True)))
    profiles = list(local_profiles) + list(members)

    context = RequestContext(request, {
        'profiles': profiles,
        'actors_without_profile': actors_wihtout_profile})
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

    if not request.POST['role'] in [role[0] for role in AssociationRole.ROLE_CHOICES]:
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
