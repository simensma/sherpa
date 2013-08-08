from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied

from association.models import Association
from user.models import User, Permission, AssociationRole
from focus.models import Actor
from core.util import current_membership_year_start

from datetime import date

def index(request):
    context = {
        'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH
    }
    return render(request, 'common/admin/users/index.html', context)

def show(request, other_user):
    other_user = User.objects.get(id=other_user)

    # Admins can assign user/admin, users can assign users
    assignable_admin = [a for a in request.user.all_associations() if a.role == 'admin']
    assignable_user = [a for a in request.user.all_associations() if a.role == 'user']
    # Don't let users assign new permissions for those that already have user status
    # Use AssociationRole for other_user, because we can't set permissions for associations that are
    # based on parent associations (to remove access to a child, you have to remove admin-permission
    # to the parent)
    other_user_associations = Association.objects.filter(associationrole__user=other_user)
    assignable_user = [a for a in assignable_user if not a in other_user_associations]
    assignable_associations = assignable_admin + assignable_user

    # Only admins can revoke association relation
    revokable_associations = [a for a in assignable_admin if a in other_user_associations]

    today = date.today()

    context = {
        'other_user': other_user,
        'revokable_associations': Association.sort(revokable_associations),
        'assignable_associations': Association.sort(assignable_associations),
        'year': today.year,
        'next_year': today >= current_membership_year_start()
    }
    return render(request, 'common/admin/users/show.html', context)

def search(request):
    if len(request.POST['q']) < settings.ADMIN_USER_SEARCH_CHAR_LENGTH:
        raise PermissionDenied

    local_users = User.objects.filter(memberid__isnull=True)
    for word in request.POST['q'].split():
        local_users = local_users.filter(
            Q(first_name__icontains=word) |
            Q(last_name__icontains=word))
    local_users = local_users.order_by('first_name')

    actors = Actor.objects.all()
    for word in request.POST['q'].split():
        actors = actors.filter(
            Q(first_name__icontains=word) |
            Q(last_name__icontains=word) |
            Q(memberid__icontains=word))
    actors = actors.order_by('first_name')

    members = User.objects.filter(memberid__in=[a.memberid for a in actors])
    actors_without_user = [a for a in actors if a.memberid not in list(members.values_list('memberid', flat=True))]
    users = list(local_users) + list(members)

    context = RequestContext(request, {
        'users': users,
        'actors_without_user': actors_without_user})
    return HttpResponse(render_to_string('common/admin/users/user_results.html', context))

def create_inactive(request, memberid):
    actor = Actor.objects.get(memberid=memberid)
    user = User(
        identifier=actor.memberid,
        memberid=actor.memberid,
        is_active=False
    )
    user.save()
    return redirect('admin.users.views.show', user.id)

def give_sherpa_access(request, user):
    if not request.user.has_perm('sherpa'):
        raise PermissionDenied

    permission = Permission.objects.get(name='sherpa')
    User.objects.get(id=user).permissions.add(permission)
    return redirect('admin.users.views.show', user)

def revoke_sherpa_access(request, user):
    if not request.user.has_perm('sherpa'):
        raise PermissionDenied

    permission = Permission.objects.get(name='sherpa')
    User.objects.get(id=user).permissions.remove(permission)
    return redirect('admin.users.views.show', user)

def make_sherpa_admin(request, user):
    if not request.user.has_perm('sherpa_admin'):
        raise PermissionDenied

    user = User.objects.get(id=user)
    permission = Permission.objects.get(name='sherpa_admin')
    user.permissions.add(permission)
    cache.delete('user.%s.all_associations' % user.id)
    cache.delete('user.%s.children_associations' % user.id)
    return redirect('admin.users.views.show', user)

def add_association_permission(request):
    user = User.objects.get(id=request.POST['user'])
    association = Association.objects.get(id=request.POST['association'])

    if not request.POST['role'] in [role[0] for role in AssociationRole.ROLE_CHOICES]:
        raise PermissionDenied

    # Verify that the user performing this action has the required permissions
    all_associations = request.user.all_associations()
    if role == 'admin':
        # Setting admin requires admin
        if not association in [a for a in all_associations if a.role == 'admin']:
            raise PermissionDenied
    elif role == 'user':
        # Any role can set user
        if not association in all_associations:
            raise PermissionDenied

    try:
        role = AssociationRole.objects.get(user=user, association=association)
        role.role = request.POST['role']
        role.save()
    except AssociationRole.DoesNotExist:
        role = AssociationRole(user=user, association=association, role=request.POST['role'])
        role.save()

    cache.delete('user.%s.all_associations' % user.id)
    cache.delete('user.%s.children_associations' % user.id)
    return redirect('admin.users.views.show', user.id)

def revoke_association_permission(request):
    user = User.objects.get(id=request.POST['user'])
    association = Association.objects.get(id=request.POST['association'])

    # Verify that the user performing this action has the required permissions
    admin_associations = [a for a in request.user.all_associations() if a.role == 'admin']
    if not association in admin_associations:
        raise PermissionDenied

    role = AssociationRole.objects.get(user=user, association=association)
    role.delete()
    cache.delete('user.%s.all_associations' % user.id)
    cache.delete('user.%s.children_associations' % user.id)
    return redirect('admin.users.views.show', user.id)
