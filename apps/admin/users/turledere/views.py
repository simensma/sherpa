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

def index(request):
    context = {
        'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH,
        'turleder_roles': Turleder.TURLEDER_CHOICES
    }
    return render(request, 'common/admin/users/turledere/index.html', context)

def edit(request, user):
    user = User.get_users().get(id=user)

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

        user.turleder_active_associations.clear()
        if json.loads(request.POST['active_associations_all']):
            user.turleder_active_associations = Association.objects.filter(type='forening')
        else:
            for association_id in json.loads(request.POST['active_association_ids']):
                user.turleder_active_associations.add(Association.objects.get(id=association_id))

        turledere = json.loads(request.POST['turledere'])
        user.turledere.exclude(id__in=[t['id'] for t in turledere if t['id'] != '']).delete()
        for turleder in turledere:
            role = turleder['role']
            if turleder['role'] not in [c[0] for c in Turleder.TURLEDER_CHOICES]:
                raise PermissionDenied

            association_approved = Association.objects.get(id=turleder['association_approved'])
            date_start = datetime.strptime(turleder['date_start'], '%d.%m.%Y').date()
            date_end = datetime.strptime(turleder['date_end'], '%d.%m.%Y').date()

            if turleder['id'] != '':
                turleder = Turleder.objects.get(id=turleder['id'])
            else:
                turleder = Turleder()

            turleder.user = user
            turleder.role = role
            turleder.association_approved = association_approved
            turleder.date_start = date_start
            turleder.date_end = date_end
            turleder.save()

        messages.info(request, "success")
        return redirect('admin.users.turledere.views.edit', user.id)

    else:
        return redirect('admin.users.turledere.views.edit')

def search(request):
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
            for i in reversed(range(0, len(Turleder.TURLEDER_CHOICES) - 1)):
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
        'html': render_to_string('common/admin/users/turledere/search_results.html', context)
    }))
