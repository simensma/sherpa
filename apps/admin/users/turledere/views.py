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
from user.models import User, Turleder
from focus.models import Actor
from user.util import create_inactive_user

def index(request):
    total_count = User.objects.filter(turledere__isnull=False).distinct().count()

    context = {
        'total_count': total_count,
        'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH
    }
    return render(request, 'common/admin/users/turledere/index.html', context)

def edit(request, user):
    user = User.objects.get(id=user)

    if request.method == 'GET':

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

        return render(request, 'common/admin/users/turledere/edit.html', context)

    elif request.method == 'POST':

        turledere = json.loads(request.POST['turledere'])
        user.turledere.exclude(id__in=[t['id'] for t in turledere if t['id'] != '']).delete()
        for turleder in turledere:
            role = turleder['role']
            if turleder['role'] not in [c[0] for c in Turleder.TURLEDER_CHOICES]:
                raise PermissionDenied

            association = Association.objects.get(id=turleder['association'])
            date_start = datetime.strptime(turleder['date_start'], '%d.%m.%Y').date()
            date_end = datetime.strptime(turleder['date_end'], '%d.%m.%Y').date()

            if turleder['id'] != '':
                turleder = Turleder.objects.get(id=turleder['id'])
            else:
                turleder = Turleder()

            turleder.user = user
            turleder.role = role
            turleder.association = association
            turleder.date_start = date_start
            turleder.date_end = date_end
            turleder.save()

        messages.info(request, "success")
        return redirect('admin.users.turledere.views.edit', user.id)

    else:
        return redirect('admin.users.turledere.views.edit')

def create_and_edit(request, memberid):
    user = create_inactive_user(memberid)
    return redirect('admin.users.turledere.views.edit', user.id)

def search(request):
    if request.POST['search_type'] == 'query':
        if len(request.POST['query']) < settings.ADMIN_USER_SEARCH_CHAR_LENGTH:
            raise PermissionDenied

        actors = Actor.objects.all()
        for word in request.POST['query'].split():
            actors = actors.filter(
                Q(first_name__icontains=word) |
                Q(last_name__icontains=word) |
                Q(memberid__icontains=word))

        turledere = User.objects.filter(turledere__isnull=False, memberid__in=[a.memberid for a in actors]).distinct().prefetch_related('turledere', 'turledere__association')
        users = sorted(turledere, key=lambda u: u.get_full_name())

        context = RequestContext(request, {
            'users': users,
            'query': request.POST['query'],
            'search_type': request.POST['search_type']
        })
        return HttpResponse(json.dumps({
            'complete': len(users) == 0,
            'html': render_to_string('common/admin/users/turledere/search_results.html', context)
        }))

    elif request.POST['search_type'] == 'infinite':
        BULK_COUNT = 40
        start = int(request.POST['bulk']) * BULK_COUNT
        end = start + BULK_COUNT

        # We want to sort on name, which is in Focus. Actors are cached, so this will only be slow once.
        # Note that the *first request* will be slow, after sorting all turledere once.
        turledere = User.objects.filter(turledere__isnull=False)
        association = None
        if request.POST['turleder_association'] != '':
            association = Association.objects.get(id=request.POST['turleder_association'])
            turledere = turledere.filter(turledere__association=association)
        turledere = turledere.distinct().prefetch_related('turledere', 'turledere__association')
        users = sorted(turledere, key=lambda u: u.get_full_name())[start:end]

        context = RequestContext(request, {
            'users': users,
            'search_type': request.POST['search_type'],
            'association': association,
            'first_bulk': request.POST['bulk'] == '0'
        })
        return HttpResponse(json.dumps({
            'complete': len(users) == 0,
            'html': render_to_string('common/admin/users/turledere/search_results.html', context)
        }))
