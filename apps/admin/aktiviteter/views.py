from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from django.contrib.gis.geos import Point
from django.contrib import messages

from aktiviteter.models import Aktivitet, AktivitetDate, AktivitetImage
from core.models import Tag, County, Municipality
from sherpa2.models import Location
from user.models import User
from focus.models import Actor
from association.models import Association

from datetime import datetime
import json

def index(request):
    aktiviteter = Aktivitet.objects.all()

    if not (request.GET.get('forening') == 'alle' and request.user.has_perm('sherpa_admin')):
        aktiviteter = aktiviteter.filter(
            Q(association=request.session['active_association']) |
            Q(co_association=request.session['active_association'])
        )
        exclude_filter = False
    else:
        exclude_filter = True

    aktiviteter = aktiviteter.order_by('-pub_date')

    context = {
        'aktiviteter': aktiviteter,
        'exclude_filter': exclude_filter,
    }
    return render(request, 'common/admin/aktiviteter/index.html', context)

def new(request):
    aktivitet = Aktivitet(
        association=request.session['active_association'],
        pub_date=datetime.now(),
        category=Aktivitet.CATEGORY_CHOICES[0][0],
        audiences=json.dumps([]),
        locations=json.dumps([]),
    )
    aktivitet.save()
    return redirect('admin.aktiviteter.views.edit', aktivitet.id)

def edit(request, aktivitet):
    if request.method == 'GET':
        aktivitet = Aktivitet.objects.prefetch_related('municipalities', 'counties').get(id=aktivitet)
        context = {
            'aktivitet': aktivitet,
            'difficulties': Aktivitet.DIFFICULTY_CHOICES,
            'audiences': Aktivitet.AUDIENCE_CHOICES,
            'categories': Aktivitet.CATEGORY_CHOICES,
            'subcategories': Aktivitet.SUBCATEGORIES,
            'all_associations': Association.sort(Association.objects.all()),
            'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH,
            'counties': County.typical_objects().order_by('name'),
            'municipalities': Municipality.objects.order_by('name'),
            'locations': Location.get_active().order_by('name'),
            'now': datetime.now()
        }
        return render(request, 'common/admin/aktiviteter/edit/edit.html', context)
    elif request.method == 'POST':
        errors = False

        aktivitet = Aktivitet.objects.get(id=aktivitet)
        aktivitet.code = request.POST['code']
        aktivitet.title = request.POST['title']
        aktivitet.description = request.POST['description']
        aktivitet.difficulty = request.POST['difficulty']
        aktivitet.audiences = json.dumps(request.POST.getlist('audiences'))
        aktivitet.category = request.POST['category']
        aktivitet.published = request.POST.get('publish') == 'publish'
        aktivitet.getting_there = request.POST['getting_there']
        aktivitet.locations = json.dumps([int(l) for l in request.POST.getlist('locations')])

        if aktivitet.published:
            # If published, set the extra relevant fields (otherwise ignore them)
            aktivitet.private = json.loads(request.POST['private'])
            try:
                aktivitet.pub_date = datetime.strptime(request.POST['pub_date'], "%d.%m.%Y").date()
            except ValueError:
                errors = True
                messages.error(request, 'invalid_date_format')

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

        aktivitet.counties = request.POST.getlist('counties')
        aktivitet.municipalities = request.POST.getlist('municipalities')

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

            try:
                aktivitet_date.start_date = datetime.strptime("%s %s" % (date_post['start_date'], date_post['start_time']), "%d.%m.%Y %H:%M")
                aktivitet_date.end_date = datetime.strptime("%s %s" % (date_post['end_date'], date_post['end_time']), "%d.%m.%Y %H:%M")
                if date_post['signup_type'] == 'minside' or date_post['signup_type'] == 'simple':
                    aktivitet_date.signup_enabled = True
                    aktivitet_date.signup_start = datetime.strptime(date_post['signup_start'], "%d.%m.%Y").date()
                    if date_post['signup_deadline_until_start']:
                        aktivitet_date.signup_deadline = aktivitet_date.start_date
                    else:
                        aktivitet_date.signup_deadline = datetime.strptime(date_post['signup_deadline'], "%d.%m.%Y").date()
                    if date_post['signup_cancel_deadline_until_start']:
                        aktivitet_date.signup_cancel_deadline = aktivitet_date.start_date
                    else:
                        aktivitet_date.signup_cancel_deadline = datetime.strptime(date_post['signup_cancel_deadline'], "%d.%m.%Y").date()
                elif date_post['signup_type'] == 'none':
                    aktivitet_date.signup_enabled = False
                    aktivitet_date.signup_start = None
                    aktivitet_date.signup_deadline = None
                    aktivitet_date.signup_cancel_deadline = None
                else:
                    raise Exception("Unrecognized POST value for signup_type field")
            except ValueError:
                errors = True
                messages.error(request, 'invalid_date_format')

            aktivitet_date.signup_simple_allowed = date_post['signup_type'] == 'simple'
            aktivitet_date.meeting_place = date_post['meeting_place']
            aktivitet_date.contact_type = date_post['contact_type']
            aktivitet_date.contact_custom_name = date_post['contact_custom_name']
            aktivitet_date.contact_custom_phone = date_post['contact_custom_phone']
            aktivitet_date.contact_custom_email = date_post['contact_custom_email']
            aktivitet_date.save()

            # Turledere
            aktivitet_date.turledere = date_post['turledere']

        if not errors:
            messages.info(request, 'save_success')

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
        'all': fake_date_representation['turledere']
    }
    context = RequestContext(request, {
        'date': fake_date_representation
    })
    return HttpResponse(json.dumps({
        'html': render_to_string('common/admin/aktiviteter/edit/dates_view.html', context),
    }))

def delete_date_preview(request):
    try:
        aktivitet_date = AktivitetDate.objects.get(id=request.POST['date'])
    except (AktivitetDate.DoesNotExist, ValueError):
        aktivitet_date = None

    context = RequestContext(request, {
        'date': aktivitet_date
    })
    return HttpResponse(json.dumps({
        'html': render_to_string('common/admin/aktiviteter/edit/dates_delete.html', context),
    }))

def participants(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    context = {
        'aktivitet': aktivitet
    }
    return render(request, 'common/admin/aktiviteter/participants.html', context)

def turleder_search(request):
    MAX_HITS = 100

    if len(request.POST['q']) < settings.ADMIN_USER_SEARCH_CHAR_LENGTH:
        raise PermissionDenied

    local_nonmember_users = User.get_users().filter(memberid__isnull=True)
    for word in request.POST['q'].split():
        local_nonmember_users = local_nonmember_users.filter(
            Q(first_name__icontains=word) |
            Q(last_name__icontains=word)
        )
    local_nonmember_users = local_nonmember_users.order_by('first_name')

    actors = Actor.objects.all()
    for word in request.POST['q'].split():
        actors = actors.filter(
            Q(first_name__icontains=word) |
            Q(last_name__icontains=word) |
            Q(memberid__icontains=word)
        )
    actors = actors.order_by('first_name')

    # Get (or create) the user objects for the first MAX_HITS actor-hits
    users = [User.get_or_create_inactive(a.memberid) for a in actors[:MAX_HITS]]

    # Merge with non-members
    users = sorted(list(users) + list(local_nonmember_users), key=lambda u: u.get_full_name())

    context = RequestContext(request, {
        'users': users[:MAX_HITS]
    })
    return HttpResponse(json.dumps({
        'results': render_to_string('common/admin/aktiviteter/edit/turleder_search_results.html', context),
        'max_hits_exceeded': len(users) > MAX_HITS or len(actors) > MAX_HITS
    }))
