from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string
from django.db.models import Q

from datetime import datetime, date
import json

from association.models import Association
from user.models import Profile, Turleder
from focus.models import Actor
from admin.turledere.models import ProfileWrapper
from user.util import create_inactive_user

def index(request):
    total_count = Profile.objects.filter(turledere__isnull=False).distinct().count()

    context = {
        'total_count': total_count,
        'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH
    }
    return render(request, 'common/admin/turledere/index.html', context)

def edit(request, profile):
    profile = Profile.objects.get(id=profile)

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
            'profile': profile,
            'turleder_roles': Turleder.TURLEDER_CHOICES,
            'all_associations': Association.sort(Association.objects.all()),
            'today': today,
            'five_years_from_now': five_years_from_now,
        }

        return render(request, 'common/admin/turledere/edit.html', context)

    elif request.method == 'POST':

        turledere = json.loads(request.POST['turledere'])
        profile.turledere.exclude(id__in=[t['id'] for t in turledere if t['id'] != '']).delete()
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

            turleder.profile = profile
            turleder.role = role
            turleder.association = association
            turleder.date_start = date_start
            turleder.date_end = date_end
            turleder.save()

        messages.info(request, "success")
        return HttpResponseRedirect(reverse('admin.turledere.views.edit', args=[profile.id]))

    else:
        return HttpResponseRedirect(reverse('admin.turledere.views.edit'))

def create_and_edit(request, memberid):
    profile = create_inactive_user(memberid)
    return HttpResponseRedirect(reverse('admin.turledere.views.edit', args=[profile.id]))

def search(request):
    if request.POST['search_type'] != 'all' and len(request.POST['query']) < settings.ADMIN_USER_SEARCH_CHAR_LENGTH:
        raise PermissionDenied

    actors = Actor.objects.all()
    for word in request.POST['query'].split():
        actors = actors.filter(
            Q(first_name__icontains=word) |
            Q(last_name__icontains=word) |
            Q(memberid__icontains=word))

    if request.POST['search_type'] == 'turledere':
        turledere = Profile.objects.filter(turledere__isnull=False, memberid__in=[a.memberid for a in actors])
        profiles = sorted(turledere, key=lambda p: p.get_full_name())
    elif request.POST['search_type'] == 'members':
        members = Profile.objects.filter(memberid__in=[a.memberid for a in actors])
        actors_without_profile = [ProfileWrapper(a, a.memberid) for a in actors if a.memberid not in list(members.values_list('memberid', flat=True))]
        profiles = sorted(list(members) + list(actors_without_profile), key=lambda p: p.get_full_name())
    elif request.POST['search_type'] == 'all':
        turledere = Profile.objects.filter(turledere__isnull=False).distinct().prefetch_related('turledere', 'turledere__association')
        profiles = sorted(list(turledere), key=lambda p: p.get_actor().get_full_name())

    context = RequestContext(request, {
        'profiles': profiles,
        'search_type': request.POST['search_type'],
        'query': request.POST['query']
    })
    return HttpResponse(render_to_string('common/admin/turledere/search_results.html', context))
