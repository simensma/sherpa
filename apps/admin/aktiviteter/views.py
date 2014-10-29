# encoding: utf-8
from datetime import datetime, date, timedelta
import json
import re

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from django.contrib.gis.geos import Point
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from aktiviteter.models import Aktivitet, AktivitetDate, AktivitetImage, Cabin
from admin.aktiviteter.util import parse_html_array
from core.models import Tag, County, Municipality
from sherpa2.models import Location, Turforslag, Activity as Sherpa2Aktivitet
from sherpa2.exceptions import ConversionImpossible
from user.models import User
from focus.models import Actor
from foreninger.models import Forening

def index(request):
    try:
        forening = Forening.objects.get(id=request.GET.get('forening'))
    except (ValueError, Forening.DoesNotExist):
        forening = request.active_forening

    # Check if user has access to the chosen forening. If not we set it to
    # current forening.
    if forening not in request.user.all_foreninger():
        forening = request.active_forening

    datoer = AktivitetDate.objects.all()

    if request.GET.get('sok'):
        datoer = datoer.filter(
            Q(aktivitet__title__contains=request.GET.get('sok')) |
            Q(aktivitet__code=request.GET.get('sok'))
        )

    if request.GET.get('kladd') == "false":
        datoer = datoer.filter(aktivitet__published=True)

    today = date.today()
    if request.GET.get('tid') in ['denne_uke', 'neste_uke', 'neste_maned']:
        if request.GET.get('tid') == 'denne_uke':
            start = today - timedelta(days=today.weekday())
            end = today + timedelta(days=-start.weekday(), weeks=1)

        elif request.GET.get('tid') == 'neste_uke':
            start = today + timedelta(days=-today.weekday(), weeks=1)
            end = today + timedelta(days=-today.weekday(), weeks=2)

        else:
            (start_year, start_month) = divmod(today.month, 12)
            (end_year, end_month) = divmod(today.month + 1, 12)

            start = today.replace(year=today.year+start_year, month=start_month + 1, day=1)
            end = today.replace(year=today.year+end_year, month=end_month + 1, day=1)

        datoer = datoer.filter(start_date__gte=start, start_date__lt=end)
    elif request.GET.get('tid') != 'alle':
        datoer = datoer.filter(start_date__gte=today)

    datoer = datoer.order_by('start_date')

    # Only admin should have access to children groups. This will potentially be
    # confusing for users who have access to several groups without being admin.
    if request.user.is_admin_in_forening(request.active_forening):
        children = request.active_forening.get_children_sorted()
        datoer = datoer.filter(
            Q(aktivitet__forening=forening) |
            Q(aktivitet__co_foreninger=forening) |
            Q(
                aktivitet__forening__parents=forening,
                aktivitet__forening__type='turgruppe',
            ) |
            Q(
                aktivitet__co_foreninger__parents=forening,
                aktivitet__co_foreninger__type='turgruppe',
            )
        )
    else:
        children = dict()
        datoer = datoer.filter(
            Q(aktivitet__forening=forening) |
            Q(aktivitet__co_foreninger=forening)
        )

    paginator = Paginator(datoer, 25)
    try:
        datoer = paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        datoer = paginator.page(1)
    except EmptyPage:
        datoer = paginator.page(paginator.num_pages)

    context = {
        'active_forening_children': children,
        'selected_forening': forening,
        'datoer': datoer,
        'params': {
            'sok': request.GET.get('sok'),
            'tid': request.GET.get('tid'),
            'kladd': request.GET.get('kladd')
        },
    }
    return render(request, 'common/admin/aktiviteter/index.html', context)

def new(request):
    aktivitet = Aktivitet(
        forening=request.active_forening,
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
            'all_foreninger': Forening.get_all_sorted(),
            'cabins': Cabin.objects.order_by('name'),
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

        if aktivitet.is_imported():
            # Should only be possible by circumventing client-side restrictions
            return redirect('admin.aktiviteter.views.edit', aktivitet.id)

        if 'code' in request.POST:
            aktivitet.code = request.POST['code']

        if 'title' in request.POST:
            aktivitet.title = request.POST['title']

        if 'description' in request.POST:
            aktivitet.description = request.POST['description']

        if 'difficulty' in request.POST:
            aktivitet.difficulty = request.POST['difficulty']

        if 'audiences' in request.POST:
            aktivitet.audiences = json.dumps(request.POST.getlist('audiences'))

        if 'category' in request.POST:
            aktivitet.category = request.POST['category']

        if 'category_type' in request.POST:
            aktivitet.category_type = request.POST['category_type']

        if 'publish' in request.POST:
            aktivitet.published = request.POST.get('publish') == 'publish'

        if 'getting_there' in request.POST:
            aktivitet.getting_there = request.POST['getting_there']

        if 'locations' in request.POST:
            aktivitet.locations = json.dumps([int(l) for l in request.POST.getlist('locations')])

        if 'ntb_id' not in request.POST or request.POST['ntb_id'] == '':
            aktivitet.turforslag = None
        else:
            aktivitet.turforslag = request.POST['ntb_id']

        if aktivitet.published:
            # If published, set the extra relevant fields (otherwise ignore them)
            aktivitet.private = request.POST['private'] == 'private'
            try:
                aktivitet.pub_date = datetime.strptime(request.POST['pub_date'], "%d.%m.%Y").date()
            except ValueError:
                errors = True
                messages.error(request, 'invalid_date_format')

        forening_type, forening_id = request.POST['forening'].split(':')
        if forening_type == 'forening':
            forening = Forening.objects.get(id=forening_id)
            if not forening in request.user.children_foreninger():
                raise PermissionDenied
            aktivitet.forening = forening
        elif forening_type == 'cabin':
            aktivitet.forening_cabin = Cabin.objects.get(id=forening_id)
        else:
            raise PermissionDenied

        if 'co_foreninger[]' in request.POST and request.POST['co_foreninger[]'] != '':
            co_foreninger = []
            co_foreninger_cabin = []
            for co_forening in request.POST.getlist('co_foreninger[]'):
                type, id = co_forening.split(':')
                if type == 'forening':
                    co_foreninger.append(id)
                elif type == 'cabin':
                    co_foreninger_cabin.append(id)
                else:
                    raise PermissionDenied

            aktivitet.co_foreninger = co_foreninger
            aktivitet.co_foreninger_cabin = co_foreninger_cabin
        else:
            aktivitet.co_foreninger = []
            aktivitet.co_foreninger_cabin = []

        if request.POST['latlng']:
            latlng = request.POST['latlng'].split(',')
            if len(latlng) == 2:
                aktivitet.start_point = Point(float(latlng[0]), float(latlng[1]))

        aktivitet.save()

        aktivitet.counties = request.POST.getlist('counties')
        aktivitet.municipalities = request.POST.getlist('municipalities')

        aktivitet.category_tags.clear()
        if 'category_tags' in request.POST and request.POST['category_tags'] != '':
            for tag in request.POST.getlist('category_tags'):
                obj, created = Tag.objects.get_or_create(name=tag)
                aktivitet.category_tags.add(obj)

        aktivitet.images.all().delete()
        for i, image in parse_html_array(request.POST, 'images').items():
            AktivitetImage(
                aktivitet=aktivitet,
                url=image['url'],
                text=image['description'],
                photographer=image['photographer'],
                order=i
            ).save()

        dates = parse_html_array(request.POST, 'dates').items()

        # Remove the date objects that were explicitly deleted (checks and verifications are done
        # client-side). Verify that those that would be implicitly deleted (by not being POSTed for
        # editing) match those explicitly POSTed.
        date_ids = [int(d['id']) for k, d in dates if d['id'] != '']
        implicit_del = set([date.id for date in aktivitet.dates.all() if date.id not in date_ids])

        if len(implicit_del) > 0:
            # Better to raise an exception and not delete anything. The user will be confused and
            # lose edits, but we'll get a report and hopefully be able to fix this, if it ever
            # happens.
            raise Exception("Implicit delete of AktivitetDate is strictly forbidden!")

        for i, date in dates:
            if date['id'] != '':
                # @TODO Check if this can be exploited. Can you hijack another trip's date by
                # setting an arbitrary ID in the date['id'] field?
                model = AktivitetDate.objects.get(id=date['id'])
            else:
                model = AktivitetDate(aktivitet=aktivitet)

            # @TODO for existing dates; if model.start_date > now; dissalow editing.

            # Explicit delete of dates
            if date['status'] == 'delete':
                if date['id'] != '':
                    if model.total_signup_count() > 0:
                        raise Exception("Date with participants can not be deleted!")
                    model.delete()
                continue

            try:
                if not date['start_time']: date['start_time'] = '08:00'
                if not date['end_time']: date['end_time'] = '16:00'

                # @TODO check start_time > now
                model.start_date = datetime.strptime(
                    "%s %s" % (date['start_date'], date['start_time']),
                    "%d.%m.%Y %H:%M"
                )

                # @TODO check end_time > start_time
                model.end_date = datetime.strptime(
                    "%s %s" % (date['end_date'], date['end_time']),
                    "%d.%m.%Y %H:%M"
                )

                # @TODO check start_date > meeting_time
                if date['start_date'] and date['meeting_time']:
                    model.meeting_time = datetime.strptime(
                        "%s %s" % (date['start_date'], date['meeting_time']),
                        "%d.%m.%Y %H:%M"
                    )

                if not date['signup_method'] or date['signup_method'] == 'none':
                    # To the next maintainer. This block indicates that a date does not allow
                    # signup. However, keep in mind that this might be an existing date with
                    # participants. Hence, do not set model.participant to None event though it
                    # might be tempting!

                    model.signup_enabled = False
                    model.signup_start = None
                    model.signup_deadline = None
                    model.signup_cancel_deadline = None

                elif date['signup_method'] == 'minside' or date['signup_method'] == 'simple':
                    model.signup_enabled = True

                    if date.get('signup_max_allowed_limited'):
                        model.signup_max_allowed = date['signup_max_allowed']
                    else:
                        model.signup_max_allowed = None

                    if 'signup_start' in date and date['signup_start'] != '':
                        model.signup_start = datetime.strptime(
                            date['signup_start'],
                            "%d.%m.%Y"
                        ).date()
                    else:
                        model.signup_start = datetime.now()

                    if 'no_signup_deadline' in date and date['no_signup_deadline'] == '1':
                        model.signup_deadline = None
                    elif 'signup_deadline' in date and date['signup_deadline'] != '':
                        model.signup_deadline = datetime.strptime(
                            date['signup_deadline'],
                            "%d.%m.%Y"
                        ).date()

                    if 'no_cancel_deadline' in date and date['no_cancel_deadline'] == '1':
                        model.signup_cancel_deadline = None
                    elif 'cancel_deadline' in date and date['cancel_deadline'] != '':
                        model.signup_cancel_deadline = datetime.strptime(
                            date['cancel_deadline'], "%d.%m.%Y"
                        ).date()

                else:
                    raise Exception("Unrecognized POST value for signup_method field")

            except ValueError:
                errors = True
                messages.error(request, 'invalid_date_format')
                return redirect('admin.aktiviteter.views.edit', aktivitet.id)

            model.signup_simple_allowed = date['signup_method'] == 'simple'
            model.meeting_place = date['meeting_place']
            model.contact_type = date['contact_type']
            model.contact_custom_name = date['contact_custom_name']
            model.contact_custom_phone = date['contact_custom_phone']
            model.contact_custom_email = date['contact_custom_email']
            model.should_have_turleder = date.get('should_have_turleder') == '1'
            model.save()

            if date.get('should_have_turleder') == '1':
                # We need to specify the key for this particular field because the parse_html_array
                # function does not properly parse multidimensional arrays.
                key = 'dates[%s][turleder][]' % i
                if key in request.POST and request.POST[key] != '':
                    model.turledere = request.POST.getlist(key)
            else:
                model.turledere = []

        if not errors:
            messages.info(request, 'save_success')

        if json.loads(request.POST['preview']):
            return redirect('admin.aktiviteter.views.preview', aktivitet.id)
        else:
            return redirect('admin.aktiviteter.views.edit', aktivitet.id)

def preview(request, aktivitet):
    try:
        aktivitet = Aktivitet.objects.get(id=aktivitet)
        aktivitet_date = aktivitet.get_dates_ordered()[0]
    except IndexError:
        context = {
            'aktivitet': aktivitet
        }
        return render(request, 'common/aktiviteter/show/preview_no_dates.html', context)

    context = {
        'aktivitet_date': aktivitet_date,
        'user_is_participating': request.user.is_authenticated() and request.user in aktivitet_date.participants.all()
    }
    return render(request, 'common/aktiviteter/show/preview.html', context)

def trigger_import(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    if not aktivitet.is_imported():
        messages.error(request, 'cannot_import_unimported_aktivitet')
        return redirect('admin.aktiviteter.views.edit', aktivitet.id)

    try:
        old_activity = Sherpa2Aktivitet.objects.get(id=aktivitet.sherpa2_id)
        old_activity.convert(aktivitet)
        messages.success(request, 'import_success')
    except ConversionImpossible:
        messages.error(request, 'conversion_impossible')
    return redirect('admin.aktiviteter.views.edit', aktivitet.id)

def turforslag_search(request):
    query = request.GET['q'].strip()

    # Trips are stored with HTML entities, so convert the query.
    # No, the re.I flag doesn't work for these characters.
    query = re.sub(u'æ', '&aelig;', query)
    query = re.sub(u'ø', '&oslash;', query)
    query = re.sub(u'å', '&aring;', query)
    query = re.sub(u'Æ', '&AElig;', query)
    query = re.sub(u'Ø', '&Oslash;', query)
    query = re.sub(u'Å', '&Aring;', query)

    if len(query) < 5:
        raise PermissionDenied

    turforslag = Turforslag.objects.all()
    for name in query.split():
        turforslag = turforslag.filter(name__icontains=name)

    turforslag = turforslag.distinct('name').order_by('name')[:12]
    turforslag = [{
        'id': t.id,
        'value': t.name,
        'tokens': t.name.split()
    } for t in turforslag]

    return HttpResponse(json.dumps(turforslag))

def edit_date_preview(request):
    # So this is kind of silly, we'll create a dict representing an AktivitetDate object so that
    # we can render the dates_view template like it normally is.
    fake_date_representation = json.loads(request.POST['date'])
    try:
        fake_date_representation['start_date'] = datetime.strptime(fake_date_representation['start_date'], "%d.%m.%Y")
        fake_date_representation['end_date'] = datetime.strptime(fake_date_representation['end_date'], "%d.%m.%Y")
    except ValueError:
        # This isn't a big problem for the preview, so just return an error at this point - the client-side will handle it
        raise PermissionDenied
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

    actors = Actor.get_personal_members()
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

def failed_imports(request):
    return render(request, 'common/admin/aktiviteter/failed_imports.html')
