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

from datetime import datetime
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
    return redirect('admin.aktiviteter.views.edit', aktivitet.id)

def edit(request, aktivitet):
    if request.method == 'GET':
        aktivitet = Aktivitet.objects.get(id=aktivitet)
        context = {
            'aktivitet': aktivitet,
            'difficulties': Aktivitet.DIFFICULTY_CHOICES,
            'audiences': Aktivitet.AUDIENCE_CHOICES,
            'subcategories': json.dumps(Aktivitet.SUBCATEGORIES[aktivitet.category]),
            'all_associations': Association.sort(Association.objects.all()),
            'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH
        }
        return render(request, 'common/admin/aktiviteter/edit/edit.html', context)
    elif request.method == 'POST':
        # TODO: Server-side validations
        aktivitet = Aktivitet.objects.get(id=aktivitet)
        aktivitet.code = request.POST['code']
        aktivitet.title = request.POST['title']
        aktivitet.description = request.POST['description']
        aktivitet.difficulty = request.POST['difficulty']
        aktivitet.audiences = json.dumps(request.POST.getlist('audiences'))
        aktivitet.pub_date = datetime.strptime(request.POST['pub_date'], "%d.%m.%Y").date()
        aktivitet.hidden = json.loads(request.POST['hidden'])
        aktivitet.getting_there = request.POST['getting_there']

        association = Association.objects.get(id=request.POST['association'])
        if not association in request.user.children_associations():
            raise PermissionDenied
        if request.POST['co_association'] == '':
            co_association = None
        else:
            co_association = Association.objects.get(id=request.POST['co_association'])

        aktivitet.association = association
        aktivitet.co_association = co_association

        if request.POST['position_lat'] != '' and request.POST['position_lng'] != '':
            aktivitet.start_point = Point(float(request.POST['position_lat']), float(request.POST['position_lng']))

        aktivitet.save()

        aktivitet.category_tags.clear()
        for tag in [tag.lower() for tag in json.loads(request.POST['subcategories'])]:
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

        #
        # Dates
        #

        dates = json.loads(request.POST['dates'])

        # Remove the date objects that were explicitly deleted (checks and verifications are
        # done client-side). Verify that those that would be implicitly deleted (by not being
        # POSTed for editing) match those explicitly POSTed.
        posted_ids = [int(d['id']) for d in dates if d['id'] != '']
        implicit_to_delete = set([date.id for date in aktivitet.dates.all() if date.id not in posted_ids])
        explicit_to_delete = set([int(d) for d in json.loads(request.POST['dates_to_delete'])])

        if implicit_to_delete != explicit_to_delete:
            # Better to raise an exception and not delete anything. The user will be confused and
            # lose edits, but we'll get a report and hopefully be able to fix this, if it ever happens.
            raise Exception("The explicit and implicit dates to delete did not match.")

        AktivitetDate.objects.filter(id__in=explicit_to_delete).delete()

        for date_post in dates:
            if date_post['id'] != '':
                aktivitet_date = AktivitetDate.objects.get(id=date_post['id'])
            else:
                aktivitet_date = AktivitetDate(aktivitet=aktivitet)

            aktivitet_date.start_date = datetime.strptime("%s %s" % (date_post['start_date'], date_post['start_time']), "%d.%m.%Y %H:%M")
            aktivitet_date.end_date = datetime.strptime("%s %s" % (date_post['end_date'], date_post['end_time']), "%d.%m.%Y %H:%M")
            if date_post['signup_type'] == 'minside' or date_post['signup_type'] == 'simple':
                aktivitet_date.signup_enabled = True
                aktivitet_date.signup_start = datetime.strptime(date_post['signup_start'], "%d.%m.%Y").date()
                aktivitet_date.signup_deadline = datetime.strptime(date_post['signup_deadline'], "%d.%m.%Y").date()
                aktivitet_date.signup_cancel_deadline = datetime.strptime(date_post['signup_cancel_deadline'], "%d.%m.%Y").date()
            elif date_post['signup_type'] == 'none':
                aktivitet_date.signup_enabled = False
            else:
                raise Exception("Unrecognized POST value for signup_type field")

            aktivitet_date.signup_simple_allowed = date_post['signup_type'] == 'simple'
            aktivitet_date.meeting_place = date_post['meeting_place']
            aktivitet_date.save()

            # Turledere
            aktivitet_date.turledere.clear()
            for user_id in date_post['turledere']['users']:
                aktivitet_date.turledere.add(User.objects.get(id=user_id))
            for actor_id in date_post['turledere']['actors']:
                actor = Actor.objects.get(id=actor_id)
                aktivitet_date.turledere.add(User.get_or_create_inactive(actor.memberid))

        return redirect('admin.aktiviteter.views.edit', aktivitet.id)

def edit_date_preview(request):
    # So this is kind of silly, we'll create a dict representing an AktivitetDate object so that
    # we can render the dates_view template like it normally is.
    fake_date_representation = json.loads(request.POST['date'])
    fake_date_representation['start_date'] = datetime.strptime(fake_date_representation['start_date'], "%d.%m.%Y")
    fake_date_representation['end_date'] = datetime.strptime(fake_date_representation['end_date'], "%d.%m.%Y")
    fake_date_representation['signup_enabled'] = fake_date_representation['signup_type'] == 'minside' or fake_date_representation['signup_type'] == 'simple'
    fake_date_representation['signup_simple_allowed'] = fake_date_representation['signup_type'] == 'simple'
    fake_date_representation['turledere'] = {
        'all': fake_date_representation['turledere']['users'] + fake_date_representation['turledere']['actors']
    }
    context = RequestContext(request, {
        'date': fake_date_representation
    })
    return HttpResponse(json.dumps({
        'html': render_to_string('common/admin/aktiviteter/edit/dates_view.html', context),
    }))

def participants(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    context = {
        'aktivitet': aktivitet
    }
    return render(request, 'common/admin/aktiviteter/edit/participants.html', context)

def turleder_search(request):
    MAX_HITS = 100

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
        'users': users[:MAX_HITS],
        'actors_without_user': actors_without_user[:MAX_HITS]})
    return HttpResponse(json.dumps({
        'results': render_to_string('common/admin/aktiviteter/edit/turleder_search_results.html', context),
        'max_hits_exceeded': len(users) > MAX_HITS or len(actors_without_user) > MAX_HITS
    }))
