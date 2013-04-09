from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string

from aktiviteter.models import Aktivitet, AktivitetDate
from core.models import Tag

from datetime import datetime, timedelta
import json

def index(request):
    aktiviteter = Aktivitet.objects.all()
    context = {
        'aktiviteter': aktiviteter,
        'categories': Aktivitet.CATEGORY_CHOICES
    }
    return render(request, 'common/admin/aktiviteter/index.html', context)

def new(request):
    now = datetime.now()
    one_day_from_now = now + timedelta(days=1)

    # TODO: Validations
    aktivitet = Aktivitet(
        pub_date=one_day_from_now,
        category=request.POST['category']
    )
    aktivitet.save()
    create_aktivitet_date(aktivitet)
    return HttpResponseRedirect(reverse('admin.aktiviteter.views.edit', args=[aktivitet.id]))

def edit(request, aktivitet):
    if request.method == 'GET':
        aktivitet = Aktivitet.objects.get(id=aktivitet)
        context = {
            'aktivitet': aktivitet,
            'difficulties': Aktivitet.DIFFICULTY_CHOICES
        }
        return render(request, 'common/admin/aktiviteter/edit.html', context)
    elif request.method == 'POST':
        # TODO: Server-side validations
        aktivitet = Aktivitet.objects.get(id=aktivitet)
        aktivitet.title = request.POST['title']
        aktivitet.description = request.POST['description']
        aktivitet.difficulty = request.POST['difficulty']
        aktivitet.pub_date = datetime.strptime(request.POST['pub_date'], "%d.%m.%Y").date()
        aktivitet.hidden = json.loads(request.POST['hidden'])
        aktivitet.save()
        aktivitet.category_tags.clear()
        for tag in [tag.lower() for tag in json.loads(request.POST['tags'])]:
            obj, created = Tag.objects.get_or_create(name=tag)
            aktivitet.category_tags.add(obj)
        return HttpResponseRedirect(reverse('admin.aktiviteter.views.edit', args=[aktivitet.id]))

def new_aktivitet_date(request):
    aktivitet = Aktivitet.objects.get(id=request.POST['aktivitet'])
    aktivitet_date = create_aktivitet_date(aktivitet)
    context = RequestContext(request, {'date': aktivitet_date})
    date_form = render_to_string('common/admin/aktiviteter/date-form.html', context)
    return HttpResponse(json.dumps(date_form))

def edit_aktivitet_date(request, aktivitet_date):
    aktivitet_date = AktivitetDate.objects.get(id=aktivitet_date)
    aktivitet_date.start_date = datetime.strptime("%s %s" % (request.POST['start_date'], request.POST['start_time']), "%d.%m.%Y %H:%M")
    aktivitet_date.end_date = datetime.strptime("%s %s" % (request.POST['end_date'], request.POST['end_time']), "%d.%m.%Y %H:%M")
    aktivitet_date.signup_enabled = json.loads(request.POST['signup_enabled'])
    if aktivitet_date.signup_enabled:
        aktivitet_date.signup_start = datetime.strptime(request.POST['signup_start'], "%d.%m.%Y").date()
        aktivitet_date.signup_deadline = datetime.strptime(request.POST['signup_deadline'], "%d.%m.%Y").date()
        aktivitet_date.signup_cancel_deadline = datetime.strptime(request.POST['signup_cancel_deadline'], "%d.%m.%Y").date()
    aktivitet_date.save()
    context = RequestContext(request, {'date': aktivitet_date})
    date_form = render_to_string('common/admin/aktiviteter/date-form.html', context)
    return HttpResponse(json.dumps(date_form))

def delete_aktivitet_date(request, aktivitet_date):
    aktivitet_date = AktivitetDate.objects.get(id=aktivitet_date)
    if aktivitet_date.aktivitet.dates.count() == 1:
        # Aktiviteter must have at least one date. This isn't enforced on the model level so it's
        # possible that if the stars align correctly, an aktivitet will end up without dates and
        # errors will occur when assuming one exists. So try to avoid that, like we're doing here.
        raise PermissionDenied
    aktivitet_date.delete()
    return HttpResponse()

def create_aktivitet_date(aktivitet):
    now = datetime.now()
    six_days_from_now = now + timedelta(days=6)
    seven_days_from_now = now + timedelta(days=7)

    aktivitet_date = AktivitetDate(
        aktivitet=aktivitet,
        start_date=now,
        end_date=seven_days_from_now,
        signup_start=now.date(),
        signup_deadline=six_days_from_now.date(),
        signup_cancel_deadline=six_days_from_now.date())
    aktivitet_date.save()
    return aktivitet_date
