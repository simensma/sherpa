from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from datetime import datetime, date, timedelta
import json

from association.models import Association
from user.models import Profile, Turleder

def index(request):
    turledere = Profile.objects.filter(turleder__isnull=False).distinct().prefetch_related('turleder', 'turleder__association')
    turledere = sorted(list(turledere), key=lambda p: p.get_actor().get_full_name())

    context = {
        'turledere': turledere
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
        profile.turleder.exclude(id__in=[t['id'] for t in turledere if t['id'] != '']).delete()
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
