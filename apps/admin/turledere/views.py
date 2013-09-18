# encoding: utf-8
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
from django.db.models import Q

from datetime import datetime, date
import json

from association.models import Association
from user.models import User, Turleder, Kursleder
from focus.models import Actor
from user.util import create_inactive_user

def index(request):
    context = {
        'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH,
        'turleder_roles': Turleder.TURLEDER_CHOICES
    }
    return render(request, 'common/admin/turledere/index.html', context)

def edit_inactive(request, memberid):
    user = create_inactive_user(memberid)
    return redirect('admin.turledere.views.edit', user.id)

def edit(request, user):
    user = User.get_users().get(id=user)

    today = date.today()
    # We can't just add 365*5 timedelta days because that doesn't account for leap years,
    # this does.
    try:
        five_years_from_now = date(year=(today.year + 5), month=today.month, day=today.day)
    except ValueError:
        # This will only occur when today is February 29th during a leap year (right?)
        five_years_from_now = date(year=(today.year + 5), month=today.month, day=(today.day-1))

    context = {
        'turleder': user,
        'turleder_roles': Turleder.TURLEDER_CHOICES,
        'all_associations': Association.sort(Association.objects.all()),
        'today': today,
        'five_years_from_now': five_years_from_now,
    }

    return render(request, 'common/admin/turledere/edit.html', context)

def edit_turleder_certificate(request, user):
    user = User.get_users().get(id=user)

    if request.POST['turleder'] != '':
        turleder = Turleder.objects.get(id=request.POST['turleder'])
    else:
        turleder = Turleder(
            user=user,
            role=request.POST['role'],
        )

    turleder.association_approved = Association.objects.get(id=request.POST['association_approved'])
    turleder.date_start = datetime.strptime(request.POST['date_start'], '%d.%m.%Y').date()
    if turleder.role == u'ambassadør':
        turleder.date_end = None
    else:
        turleder.date_end = datetime.strptime(request.POST['date_end'], '%d.%m.%Y').date()
    turleder.save()

    messages.info(request, "success")
    return redirect('admin.turledere.views.edit', user.id)

def edit_kursleder_certificate(request, user):
    if not request.user.can_modify_kursleder_status():
        raise PermissionDenied

    user = User.get_users().get(id=user)

    if request.POST['kursleder'] != '':
        kursleder = Kursleder.objects.get(id=request.POST['kursleder'])
    else:
        kursleder = Kursleder(user=user)

    kursleder.date_start = datetime.strptime(request.POST['date_start'], '%d.%m.%Y').date()
    kursleder.date_end = datetime.strptime(request.POST['date_end'], '%d.%m.%Y').date()
    kursleder.save()

    messages.info(request, "success")
    return redirect('admin.turledere.views.edit', user.id)

def edit_active_associations(request, user):
    user = User.get_users().get(id=user)

    user.turleder_active_associations.clear()
    if json.loads(request.POST['active_associations_all']):
        user.turleder_active_associations = Association.objects.filter(type='forening')
    else:
        for association_id in json.loads(request.POST['active_association_ids']):
            user.turleder_active_associations.add(Association.objects.get(id=association_id))

    messages.info(request, "success")
    return redirect('admin.turledere.views.edit', user.id)

def remove_turleder(request, turleder):
    turleder = Turleder.objects.get(id=turleder)
    user = turleder.user
    turleder.delete()
    return redirect('admin.turledere.views.edit', user.id)

def remove_kursleder(request, kursleder):
    if not request.user.can_modify_kursleder_status():
        raise PermissionDenied

    kursleder = Kursleder.objects.get(id=kursleder)
    user = kursleder.user
    kursleder.delete()
    return redirect('admin.turledere.views.edit', user.id)

def turleder_search(request):
    turledere = User.get_users().filter(turledere__isnull=False)

    if len(request.POST['query']) > 0:
        if len(request.POST['query']) < settings.ADMIN_USER_SEARCH_CHAR_LENGTH:
            raise PermissionDenied

        actors = Actor.objects.all()
        for word in request.POST['query'].split():
            actors = actors.filter(
                Q(first_name__icontains=word) |
                Q(last_name__icontains=word) |
                Q(memberid__icontains=word))

        turledere = turledere.filter(memberid__in=[a.memberid for a in actors])

    # Filter on associations where the turleder is active
    active_associations = json.loads(request.POST['turleder_associations_active'])
    if len(active_associations) > 0:
        turledere = turledere.filter(turleder_active_associations__in=active_associations)

    turleder_role = request.POST['turleder_role']
    if turleder_role != '':
        if json.loads(request.POST['turleder_role_include']):
            roles = []
            found = False
            for i in reversed(range(0, len(Turleder.TURLEDER_CHOICES))):
                if Turleder.TURLEDER_CHOICES[i][0] == turleder_role:
                    found = True
                if found:
                    roles.append(Turleder.TURLEDER_CHOICES[i][0])
        else:
            roles = [request.POST['turleder_role']]
        turledere = turledere.filter(turledere__role__in=roles)

    # Filter on certificates approved by some association
    association_approved = None
    if request.POST['turleder_association_approved'] != '':
        association_approved = Association.objects.get(id=request.POST['turleder_association_approved'])
        turledere = turledere.filter(turledere__association_approved=association_approved)

    # Clean up, prefetch and sort by name. Names must be fetched from Focus for each hit,
    # hence slow. Actors are cached, so it will only be slow once.
    BULK_COUNT = 40
    start = int(request.POST['bulk']) * BULK_COUNT
    end = start + BULK_COUNT
    turledere = turledere.distinct().prefetch_related('turledere', 'turledere__association_approved')
    total_count = turledere.count()
    turledere = sorted(turledere, key=lambda u: u.get_full_name())[start:end]

    context = RequestContext(request, {
        'users': turledere,
        'first_bulk': request.POST['bulk'] == '0',
        'total_count': total_count,
        'association_count': Association.objects.filter(type='forening').count()
    })
    return HttpResponse(json.dumps({
        'complete': len(turledere) == 0,
        'html': render_to_string('common/admin/turledere/turleder_search_results.html', context)
    }))

def member_search(request):
    if len(request.POST['query']) < settings.ADMIN_USER_SEARCH_CHAR_LENGTH:
        raise PermissionDenied

    actors = Actor.objects.all()
    for word in request.POST['query'].split():
        actors = actors.filter(
            Q(first_name__icontains=word) |
            Q(last_name__icontains=word) |
            Q(memberid__icontains=word))
    actors = actors.order_by('first_name')

    users = User.get_users().filter(memberid__in=[a.memberid for a in actors])
    actors_without_user = [a for a in actors if a.memberid not in list(users.values_list('memberid', flat=True))]
    users = sorted(users, key=lambda u: u.get_full_name())

    context = RequestContext(request, {
        'users': users,
        'actors_without_user': actors_without_user,
    })
    return HttpResponse(render_to_string('common/admin/turledere/member_search_results.html', context))
