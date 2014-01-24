from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied

from foreninger.models import Forening
from user.models import User, Permission, ForeningRole, Turleder
from focus.models import Actor, Enrollment

from datetime import date
import json

def index(request):
    context = {
        'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH
    }
    return render(request, 'common/admin/users/index.html', context)

def show(request, other_user):
    other_user = User.objects.get(id=other_user)

    # Admins can assign user/admin, users can assign users
    assignable_admin = [a for a in request.user.all_foreninger() if a.role == 'admin']
    assignable_user = [a for a in request.user.all_foreninger() if a.role == 'user']
    # Don't let users assign new permissions for those that already have user status
    # Use ForeningRole for other_user, because we can't set permissions for foreninger that are
    # based on parent foreninger (to remove access to a child, you have to remove admin-permission
    # to the parent)
    other_user_foreninger = Forening.objects.filter(foreningrole__user=other_user)
    assignable_user = [a for a in assignable_user if not a in other_user_foreninger]
    assignable_foreninger = assignable_admin + assignable_user

    # Only admins can revoke forening relation
    revokable_foreninger = [a for a in assignable_admin if a in other_user_foreninger]

    today = date.today()

    # We can't just add 365*5 timedelta days because that doesn't account for leap years,
    # this does.
    try:
        five_years_from_now = date(year=(today.year + 5), month=today.month, day=today.day)
    except ValueError:
        # This will only occur when today is February 29th during a leap year (right?)
        five_years_from_now = date(year=(today.year + 5), month=today.month, day=(today.day-1))

    context = {
        'other_user': other_user,
        'revokable_foreninger': Forening.sort(revokable_foreninger),
        'assignable_foreninger': Forening.sort(assignable_foreninger),
        'all_foreninger': Forening.sort(Forening.objects.all()),
        'turleder_roles': Turleder.TURLEDER_CHOICES,
        'today': today,
        'five_years_from_now': five_years_from_now,
    }
    return render(request, 'common/admin/users/show/index.html', context)

def search(request):
    if len(request.POST['q']) < settings.ADMIN_USER_SEARCH_CHAR_LENGTH:
        raise PermissionDenied

    local_users = User.get_users().filter(memberid__isnull=True)
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

    # Match expired users only on memberid
    expired_users = User.objects.all()
    for word in request.POST['q'].split():
        expired_users = expired_users.filter(memberid__icontains=word)
    expired_users = [u for u in expired_users if not Actor.objects.filter(memberid=u.memberid).exists()]

    # Pending users
    pending_enrollment = Enrollment.get_active()
    for word in request.POST['q'].split():
        pending_enrollment = pending_enrollment.filter(
            Q(first_name__icontains=word) |
            Q(last_name__icontains=word) |
            Q(memberid__icontains=word))
    pending_enrollment = pending_enrollment.order_by('first_name')

    members = User.get_users().filter(memberid__in=[a.memberid for a in actors])
    pending_users = User.get_users(include_pending=True).filter(memberid__in=[e.memberid for e in pending_enrollment])
    actors_without_user = [a for a in actors if a.memberid not in list(members.values_list('memberid', flat=True))]
    users = list(local_users) + list(members) + list(pending_users)

    context = RequestContext(request, {
        'users': users,
        'actors_without_user': actors_without_user,
        'expired_users': expired_users
    })
    return HttpResponse(render_to_string('common/admin/users/user_results.html', context))

def create_inactive(request, memberid):
    user = User.create_inactive_user(memberid)
    return redirect('admin.users.views.show', user.id)

def check_memberid(request):
    if not request.user.can_modify_user_memberid():
        raise PermissionDenied

    user_to_change = User.objects.get(id=request.POST['user'])
    memberid_is_equal = str(user_to_change.memberid) == request.POST['memberid'].strip()

    try:
        existing_user = User.objects.get(memberid=request.POST['memberid'])
    except (User.DoesNotExist, ValueError):
        existing_user = None

    try:
        actor = Actor.objects.get(memberid=request.POST['memberid'])
    except (Actor.DoesNotExist, ValueError):
        actor = None

    context = RequestContext(request, {
        'user_to_change': user_to_change,
        'existing_user': existing_user,
        'actor': actor,
        'memberid': request.POST['memberid'],
        'memberid_is_equal': memberid_is_equal
    })
    html = render_to_string('common/admin/users/check_memberid.html', context)
    return HttpResponse(json.dumps({
        'valid': actor is not None and not memberid_is_equal,
        'html': html
    }))

def change_memberid(request):
    if not request.user.can_modify_user_memberid():
        raise PermissionDenied

    # The Actor was already checked client-side, but verify here
    if not Actor.objects.filter(memberid=request.POST['new-memberid']).exists():
        raise PermissionDenied

    old_user = User.objects.get(id=request.POST['old-user'])
    try:
        new_user = User.objects.get(memberid=request.POST['new-memberid'])
        # Ah, the new memberid already has a user - merge them, but keep the password
        # of the new user
        new_user.merge_with(old_user) # This will delete the old user
        resulting_user = new_user
    except User.DoesNotExist:
        # Allright, just update the memberid to the new one
        old_user.identifier = request.POST['new-memberid']
        old_user.memberid = request.POST['new-memberid']
        old_user.is_expired = False
        old_user.is_pending = False
        old_user.save()
        resulting_user = old_user
    if 'purge-busticket' in request.POST:
        ticket = resulting_user.norway_bus_ticket
        ticket.delete()
    return redirect('admin.users.views.show', resulting_user.id)

def give_sherpa_access(request, user):
    if not request.user.has_perm('sherpa'):
        raise PermissionDenied

    permission = Permission.objects.get(name='sherpa')
    User.objects.get(id=user).permissions.add(permission)
    return redirect('%s#tilganger' % reverse('admin.users.views.show', args=[user]))

def revoke_sherpa_access(request, user):
    if not request.user.has_perm('sherpa'):
        raise PermissionDenied

    permission = Permission.objects.get(name='sherpa')
    User.objects.get(id=user).permissions.remove(permission)
    return redirect('%s#tilganger' % reverse('admin.users.views.show', args=[user]))

def make_sherpa_admin(request, user):
    if not request.user.has_perm('sherpa_admin'):
        raise PermissionDenied

    user = User.objects.get(id=user)
    permission = Permission.objects.get(name='sherpa_admin')
    user.permissions.add(permission)
    cache.delete('user.%s.all_foreninger' % user.id)
    cache.delete('user.%s.children_foreninger' % user.id)
    return redirect('%s#tilganger' % reverse('admin.users.views.show', args=[user.id]))

def add_forening_permission(request):
    user = User.objects.get(id=request.POST['user'])
    forening = Forening.objects.get(id=request.POST['forening'])

    if not request.POST['role'] in [role[0] for role in ForeningRole.ROLE_CHOICES]:
        raise PermissionDenied

    # Verify that the user performing this action has the required permissions
    all_foreninger = request.user.all_foreninger()
    if role == 'admin':
        # Setting admin requires admin
        if not forening in [a for a in all_foreninger if a.role == 'admin']:
            raise PermissionDenied
    elif role == 'user':
        # Any role can set user
        if not forening in all_foreninger:
            raise PermissionDenied

    try:
        role = ForeningRole.objects.get(user=user, forening=forening)
        role.role = request.POST['role']
        role.save()
    except ForeningRole.DoesNotExist:
        role = ForeningRole(user=user, forening=forening, role=request.POST['role'])
        role.save()

    cache.delete('user.%s.all_foreninger' % user.id)
    cache.delete('user.%s.children_foreninger' % user.id)
    return redirect('%s#tilganger' % reverse('admin.users.views.show', args=[user.id]))

def revoke_forening_permission(request):
    user = User.objects.get(id=request.POST['user'])
    forening = Forening.objects.get(id=request.POST['forening'])

    # Verify that the user performing this action has the required permissions
    admin_foreninger = [a for a in request.user.all_foreninger() if a.role == 'admin']
    if not forening in admin_foreninger:
        raise PermissionDenied

    role = ForeningRole.objects.get(user=user, forening=forening)
    role.delete()
    cache.delete('user.%s.all_foreninger' % user.id)
    cache.delete('user.%s.children_foreninger' % user.id)
    return redirect('%s#tilganger' % reverse('admin.users.views.show', args=[user.id]))
