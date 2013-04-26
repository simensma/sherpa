from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q

from aktiviteter.models import Aktivitet, AktivitetDate
from core.models import Tag
from user.models import Profile
from focus.models import Actor
from association.models import Association

from datetime import datetime, timedelta
import json

def index(request):
    aktiviteter = Aktivitet.objects.all()
    context = {
        'aktiviteter': aktiviteter,
        'categories': Aktivitet.CATEGORY_CHOICES,
        'subcategories': Aktivitet.SUBCATEGORIES
    }
    return render(request, 'common/admin/aktiviteter/index.html', context)

def new(request):
    # TODO: Validations
    aktivitet = Aktivitet(
        association=request.session['active_association'],
        pub_date=datetime.now(),
        category=request.POST['category']
    )
    aktivitet.save()
    for tag in [tag.lower() for tag in json.loads(request.POST['tags'])]:
        obj, created = Tag.objects.get_or_create(name=tag)
        aktivitet.category_tags.add(obj)
    return HttpResponseRedirect(reverse('admin.aktiviteter.views.edit_description', args=[aktivitet.id]))

def edit_description(request, aktivitet):
    if request.method == 'GET':
        aktivitet = Aktivitet.objects.get(id=aktivitet)
        context = {
            'aktivitet': aktivitet,
            'difficulties': Aktivitet.DIFFICULTY_CHOICES,
            'audiences': Aktivitet.AUDIENCE_CHOICES,
            'subcategories': json.dumps(Aktivitet.SUBCATEGORIES[aktivitet.category]),
        }
        return render(request, 'common/admin/aktiviteter/edit/description.html', context)
    elif request.method == 'POST':
        # TODO: Server-side validations
        aktivitet = Aktivitet.objects.get(id=aktivitet)
        aktivitet.title = request.POST['title']
        aktivitet.description = request.POST['description']
        aktivitet.difficulty = request.POST['difficulty']
        aktivitet.audiences = json.dumps(request.POST.getlist('audiences'))
        aktivitet.pub_date = datetime.strptime(request.POST['pub_date'], "%d.%m.%Y").date()
        aktivitet.hidden = json.loads(request.POST['hidden'])

        association = Association.objects.get(id=request.POST['association'])
        if not association in request.user.get_profile().children_associations():
            raise PermissionDenied
        if request.POST['co_association'] == '':
            co_association = None
        else:
            co_association = Association.objects.get(id=request.POST['co_association'])
            if not co_association in request.user.children_associations():
                raise PermissionDenied

        aktivitet.association = association
        aktivitet.co_association = co_association

        aktivitet.save()
        aktivitet.category_tags.clear()
        for tag in [tag.lower() for tag in json.loads(request.POST['tags'])]:
            obj, created = Tag.objects.get_or_create(name=tag)
            aktivitet.category_tags.add(obj)
        return HttpResponseRedirect(reverse('admin.aktiviteter.views.edit_description', args=[aktivitet.id]))

def edit_dates(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    context = {
        'aktivitet': aktivitet
    }
    return render(request, 'common/admin/aktiviteter/edit/dates.html', context)

def edit_leaders(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    context = {
        'aktivitet': aktivitet,
        'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH
    }
    return render(request, 'common/admin/aktiviteter/edit/leaders.html', context)

def edit_participants(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    context = {
        'aktivitet': aktivitet
    }
    return render(request, 'common/admin/aktiviteter/edit/participants.html', context)

def leader_search(request):
    MAX_HITS = 100

    aktivitet = Aktivitet.objects.get(id=request.POST['aktivitet'])

    if len(request.POST['q']) < settings.ADMIN_USER_SEARCH_CHAR_LENGTH:
        raise PermissionDenied

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

    members = Profile.objects.filter(memberid__in=[a.memberid for a in actors])
    actors_without_profile = [a for a in actors if a.memberid not in list(members.values_list('memberid', flat=True))]
    profiles = list(local_profiles) + list(members)

    context = RequestContext(request, {
        'aktivitet': aktivitet,
        'profiles': profiles[:MAX_HITS],
        'actors_without_profile': actors_without_profile[:MAX_HITS]})
    return HttpResponse(json.dumps({
        'results': render_to_string('common/admin/aktiviteter/edit/leader_search_results.html', context),
        'max_hits_exceeded': len(profiles) > MAX_HITS or len(actors_without_profile) > MAX_HITS
    }))

def leader_assign(request):
    profile = Profile.objects.get(id=request.POST['profile'])
    for date in request.POST.getlist('aktivitet_dates'):
        date = AktivitetDate.objects.get(id=date)
        date.leaders.add(profile)
    return HttpResponseRedirect(reverse('admin.aktiviteter.views.edit_leaders', args=[request.POST['aktivitet']]))

def leader_remove(request):
    profile = Profile.objects.get(id=request.POST['profile'])
    aktivitet_date = AktivitetDate.objects.get(id=request.POST['aktivitet_date'])
    aktivitet_date.leaders.remove(profile)
    return HttpResponseRedirect(reverse('admin.aktiviteter.views.edit_leaders', args=[aktivitet_date.aktivitet.id]))

def new_aktivitet_date(request):
    aktivitet = Aktivitet.objects.get(id=request.POST['aktivitet'])
    aktivitet_date = create_aktivitet_date(aktivitet)
    context = RequestContext(request, {'date': aktivitet_date})
    date_form = render_to_string('common/admin/aktiviteter/edit/dates_form.html', context)
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
    date_form = render_to_string('common/admin/aktiviteter/edit/dates_form.html', context)
    return HttpResponse(json.dumps(date_form))

def delete_aktivitet_date(request, aktivitet_date):
    AktivitetDate.objects.get(id=aktivitet_date).delete()
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
