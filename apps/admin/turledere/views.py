# encoding: utf-8
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.cache import cache

from datetime import datetime
import json

from foreninger.models import Forening
from user.models import User, Turleder, Kursleder, Instruktor
from focus.models import Actor

def index(request):
    context = {
        'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH,
        'turleder_roles': Turleder.TURLEDER_CHOICES,
        'instruktor_roles': Instruktor.ROLE_CHOICES
    }
    return render(request, 'common/admin/turledere/index.html', context)

def edit_inactive(request, memberid):
    user = User.create_inactive_user(memberid)
    return redirect('%s#turledersertifikat' % reverse('admin.users.views.show', args=[user.id]))

def edit_turleder_certificate(request, user):
    user = User.get_users().get(id=user)

    if not user.is_member():
        raise PermissionDenied

    if request.POST['role'] not in [r[0] for r in Turleder.TURLEDER_CHOICES]:
        raise PermissionDenied

    forening_approved = Forening.objects.get(id=request.POST['forening_approved'])
    date_start = None
    date_end = None
    try:
        date_start = datetime.strptime(request.POST['date_start'], '%d.%m.%Y').date()
        if request.POST['role'] not in [u'ambassadør', u'grunnleggende']:
            date_end = datetime.strptime(request.POST['date_end'], '%d.%m.%Y').date()
    except ValueError:
        messages.error(request, "invalid_turleder_sertifikat_date")

    if request.POST['turleder'] != '':
        # Explicit edit of existing object
        turleder = Turleder.objects.get(id=request.POST['turleder'])
        turleder.forening_approved = forening_approved
        turleder.date_start = date_start
        turleder.date_end = date_end
        turleder.save()
    else:
        # New object, but use get_or_create to avoid creating a duplicate role in case of a double-POST or something
        turleder, created = Turleder.objects.get_or_create(user=user, role=request.POST['role'], defaults={
            'forening_approved': forening_approved,
            'date_start': date_start,
            'date_end': date_end,
        })
        if not created:
            # Actually, this role already existed; update its values with the posted ones
            turleder.forening_approved = forening_approved
            turleder.date_start = date_start
            turleder.date_end = date_end
            turleder.save()

    messages.info(request, "success")
    return redirect('%s#turledersertifikat' % reverse('admin.users.views.show', args=[user.id]))

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
    return redirect('%s#turledersertifikat' % reverse('admin.users.views.show', args=[user.id]))

def edit_instruktor_roles(request, user):
    user = User.get_users().get(id=user)

    Instruktor.objects.filter(user=user).delete()
    for role in Instruktor.ROLE_CHOICES:
        if role['key'] in request.POST:
            instruktor = Instruktor(user=user, role=role['key'])
            instruktor.save()

    messages.info(request, "success")
    return redirect('%s#turledersertifikat' % reverse('admin.users.views.show', args=[user.id]))

def edit_active_foreninger(request, user):
    user = User.get_users().get(id=user)

    user.turleder_active_foreninger.clear()
    if json.loads(request.POST['active_foreninger_all']):
        user.turleder_active_foreninger = Forening.objects.filter(type='forening')
    else:
        for forening_id in json.loads(request.POST['active_forening_ids']):
            user.turleder_active_foreninger.add(Forening.objects.get(id=forening_id))

    messages.info(request, "success")
    return redirect('%s#turledersertifikat' % reverse('admin.users.views.show', args=[user.id]))

def remove_turleder(request, turleder):
    turleder = Turleder.objects.get(id=turleder)
    user = turleder.user
    turleder.delete()
    return redirect('%s#turledersertifikat' % reverse('admin.users.views.show', args=[user.id]))

def remove_kursleder(request, kursleder):
    if not request.user.can_modify_kursleder_status():
        raise PermissionDenied

    kursleder = Kursleder.objects.get(id=kursleder)
    user = kursleder.user
    kursleder.delete()
    return redirect('%s#turledersertifikat' % reverse('admin.users.views.show', args=[user.id]))

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

    # Filter on foreninger where the turleder is active
    active_foreninger = json.loads(request.POST['turleder_foreninger_active'])
    if len(active_foreninger) > 0:
        turledere = turledere.filter(turleder_active_foreninger__in=active_foreninger)

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

    for role in json.loads(request.POST['instruktor_roles']):
        turledere = turledere.filter(instruktor__role=role)

    # Filter on certificates approved by some forening
    forening_approved = None
    if request.POST['turleder_forening_approved'] != '':
        forening_approved = Forening.objects.get(id=request.POST['turleder_forening_approved'])
        turledere = turledere.filter(turledere__forening_approved=forening_approved)

    # Clean up, prefetch and sort by name. Names must be fetched from Focus for each hit,
    # hence slow. Actors are cached, so it will only be slow once.
    BULK_COUNT = 40
    start = int(request.POST['bulk']) * BULK_COUNT
    end = start + BULK_COUNT
    turledere = turledere.distinct().prefetch_related('turledere', 'turledere__forening_approved')
    total_count = turledere.count()

    # To sort them by name, we'll need the Actor data - prefetch the hits in one query, and cache them
    # Save some time by excluding actors that are already cached
    memberids = [t.memberid for t in turledere if cache.get('actor.%s' % t.memberid) is None]

    # If we have more than 2100 parameters, MSSQL will cry, so split it up in bulks
    for i in range(0, len(memberids), settings.MSSQL_MAX_PARAMETER_COUNT):
        memberid_chunk = memberids[i:i + settings.MSSQL_MAX_PARAMETER_COUNT]
        for actor in Actor.objects.filter(memberid__in=memberid_chunk):
            cache.set('actor.%s' % actor.memberid, actor, settings.FOCUS_MEMBER_CACHE_PERIOD)

    # Now it's safe to iterate without having n+1 issues - all hits should be cached
    turledere = sorted(turledere, key=lambda u: u.get_full_name())[start:end]

    context = RequestContext(request, {
        'users': turledere,
        'first_bulk': request.POST['bulk'] == '0',
        'total_count': total_count,
        'forening_count': Forening.objects.filter(type='forening').count()
    })
    return HttpResponse(json.dumps({
        'complete': len(turledere) == 0,
        'html': render_to_string('common/admin/turledere/turleder_search_results.html', context)
    }))

def member_search(request):
    if len(request.POST['query']) < settings.ADMIN_USER_SEARCH_CHAR_LENGTH:
        raise PermissionDenied

    local_users = User.get_users().filter(memberid__isnull=True)
    for word in request.POST['query'].split():
        local_users = local_users.filter(
            Q(first_name__icontains=word) |
            Q(last_name__icontains=word)
        )
    local_users = local_users.order_by('first_name')

    actors = Actor.objects.all()
    for word in request.POST['query'].split():
        actors = actors.filter(
            Q(first_name__icontains=word) |
            Q(last_name__icontains=word) |
            Q(memberid__icontains=word)
        )
    actors = actors.order_by('first_name')

    users = User.get_users().filter(memberid__in=[a.memberid for a in actors])
    memberids = [u.memberid for u in users]
    actors_without_user = [a for a in actors if a.memberid not in memberids]

    # To sort users by name, we need the Actor data - go through the already-fetched bulk and cache them
    for actor in actors:
        cache.set('actor.%s' % actor.memberid, actor, settings.FOCUS_MEMBER_CACHE_PERIOD)

    users = sorted(users, key=lambda u: u.get_full_name())

    context = RequestContext(request, {
        'users': users,
        'actors_without_user': actors_without_user,
        'local_users': local_users,
    })
    return HttpResponse(render_to_string('common/admin/turledere/member_search_results.html', context))
