from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from django.contrib.gis.geos import Point

from aktiviteter.models import Aktivitet, AktivitetDate, AktivitetImage
from core.models import Tag
from user.models import User
from focus.models import Actor
from association.models import Association
from user.util import create_inactive_user

from datetime import datetime, timedelta
import json

def index(request):
    if 'forening' in request.GET:
        association_filter = Association.objects.get(id=request.GET['forening'])
    else:
        association_filter = request.session['active_association']

    aktiviteter = Aktivitet.objects.filter(
        Q(association=association_filter) |
        Q(co_association=association_filter)
    )

    context = {
        'aktiviteter': aktiviteter,
        'categories': Aktivitet.CATEGORY_CHOICES,
        'subcategories': Aktivitet.SUBCATEGORIES,
        'association_filter': association_filter
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
    return redirect('admin.aktiviteter.views.edit_description', aktivitet.id)

def edit_description(request, aktivitet):
    if request.method == 'GET':
        aktivitet = Aktivitet.objects.get(id=aktivitet)
        context = {
            'aktivitet': aktivitet,
            'difficulties': Aktivitet.DIFFICULTY_CHOICES,
            'audiences': Aktivitet.AUDIENCE_CHOICES,
            'subcategories': json.dumps(Aktivitet.SUBCATEGORIES[aktivitet.category]),
            'all_associations': Association.sort(Association.objects.all())
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
        if not association in request.user.children_associations():
            raise PermissionDenied
        if request.POST['co_association'] == '':
            co_association = None
        else:
            co_association = Association.objects.get(id=request.POST['co_association'])

        aktivitet.association = association
        aktivitet.co_association = co_association

        aktivitet.save()

        aktivitet.category_tags.clear()
        for tag in [tag.lower() for tag in json.loads(request.POST['tags'])]:
            obj, created = Tag.objects.get_or_create(name=tag)
            aktivitet.category_tags.add(obj)

        aktivitet.images.all().delete()
        for image in json.loads(request.POST['images']):
            image = AktivitetImage(
                aktivitet=aktivitet,
                url=image['url'],
                text=image['text'],
                photographer=image['photographer'],
                order=image['order']
            )
            image.save()

        return redirect('admin.aktiviteter.views.edit_description', aktivitet.id)

def edit_position(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)

    if request.method == 'GET':
        context = {
            'aktivitet': aktivitet
        }
        return render(request, 'common/admin/aktiviteter/edit/position.html', context)
    elif request.method == 'POST':
        aktivitet.start_point = Point(float(request.POST['lat']), float(request.POST['lng']))
        aktivitet.save()
        return redirect('admin.aktiviteter.views.edit_position', aktivitet.id)

def edit_simple_signup(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    aktivitet.allow_simple_signup = json.loads(request.POST['allow_simple_signup'])
    aktivitet.save()
    return HttpResponse()

def edit_dates(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    context = {
        'aktivitet': aktivitet
    }
    return render(request, 'common/admin/aktiviteter/edit/dates.html', context)

def edit_turledere(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    context = {
        'aktivitet': aktivitet,
        'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH
    }
    return render(request, 'common/admin/aktiviteter/edit/turledere.html', context)

def edit_participants(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    context = {
        'aktivitet': aktivitet
    }
    return render(request, 'common/admin/aktiviteter/edit/participants.html', context)

def turleder_search(request):
    MAX_HITS = 100

    aktivitet = Aktivitet.objects.get(id=request.POST['aktivitet'])

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

    members = User.get_users().filter(memberid__in=[a.memberid for a in actors])
    actors_without_user = [a for a in actors if a.memberid not in list(members.values_list('memberid', flat=True))]
    users = list(local_users) + list(members)

    context = RequestContext(request, {
        'aktivitet': aktivitet,
        'users': users[:MAX_HITS],
        'actors_without_user': actors_without_user[:MAX_HITS]})
    return HttpResponse(json.dumps({
        'results': render_to_string('common/admin/aktiviteter/edit/turleder_search_results.html', context),
        'max_hits_exceeded': len(users) > MAX_HITS or len(actors_without_user) > MAX_HITS
    }))

def turleder_assign(request):
    if 'user' in request.POST:
        user = User.get_users().get(id=request.POST['user'])
    elif 'actor' in request.POST:
        # Create the requested user as inactive
        user = create_inactive_user(request.POST['actor'])
    else:
        raise Exception("Expected either 'user' or 'actor' in POST request")

    for date in request.POST.getlist('aktivitet_dates'):
        date = AktivitetDate.objects.get(id=date)
        date.turledere.add(user)
    return redirect('admin.aktiviteter.views.edit_turledere', request.POST['aktivitet'])

def turleder_remove(request):
    user = User.get_users().get(id=request.POST['user'])
    aktivitet_date = AktivitetDate.objects.get(id=request.POST['aktivitet_date'])
    aktivitet_date.turledere.remove(user)
    return redirect('admin.aktiviteter.views.edit_turledere', aktivitet_date.aktivitet.id)

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
