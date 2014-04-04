# encoding: utf-8
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied

import json

from foreninger.models import Forening
from .forms import ForeningDataForm, ExistingForeningDataForm
from user.models import User, Permission, ForeningRole
from focus.models import Actor

def index(request):
    forening_users = list(User.objects.filter(foreninger=request.session['active_forening']))

    forening_users_by_parent = []

    parent_ids = [p.id for p in request.session['active_forening'].get_parents_deep()]
    forening_users_by_parent_all = list(User.objects.filter(foreninger__in=parent_ids))

    # Prefetch and cache the actors
    memberids = [u.memberid for u in (forening_users + forening_users_by_parent)]
    for actor in Actor.objects.filter(memberid__in=memberids):
        cache.set('actor.%s' % actor.memberid, actor, settings.FOCUS_MEMBER_CACHE_PERIOD)

    # Safe to iterate without having n+1 issues

    # Filter on admins
    forening_users_by_parent = []
    for user in forening_users_by_parent_all:
        for forening in user.all_foreninger():
            if forening == request.session['active_forening'] and forening.role == 'admin':
                forening_users_by_parent.append(user)

    forening_users = sorted(forening_users, key=lambda u: u.get_full_name())
    forening_users_by_parent = sorted(forening_users_by_parent, key=lambda u: u.get_full_name())

    # The parent choices are tricky to define in the forms API, so do it here
    all_sorted = request.user.all_foreninger_sorted()
    parents_choices = {
        'foreninger': all_sorted['foreninger'],
        'turlag': all_sorted['turlag'],
    }

    context = {
        'forening_users': forening_users,
        'forening_users_by_parent': forening_users_by_parent,
        'parents_choices': parents_choices,
        'admin_user_search_char_length': settings.ADMIN_USER_SEARCH_CHAR_LENGTH
    }

    zipcode = request.session['active_forening'].zipcode
    edit_form_zipcode_area = zipcode.area if zipcode is not None else ''

    if request.session['active_forening'].contact_person is not None:
        choose_contact = 'person'
        contact_person = request.session['active_forening'].contact_person.id
        contact_person_name = request.session['active_forening'].contact_person.get_full_name()
        phone = request.session['active_forening'].contact_person.get_phone_mobile()
        email = request.session['active_forening'].contact_person.get_sherpa_email()
    elif request.session['active_forening'].contact_person_name != '':
        choose_contact = 'person'
        contact_person = None
        contact_person_name = request.session['active_forening'].contact_person_name
        phone = request.session['active_forening'].phone
        email = request.session['active_forening'].email
    else:
        choose_contact = 'forening'
        contact_person = None
        contact_person_name = ''
        phone = request.session['active_forening'].phone
        email = request.session['active_forening'].email

    edit_form = ExistingForeningDataForm(request.user, prefix='edit', initial={
        'forening': request.session['active_forening'].id,
        'parents': request.session['active_forening'].parents.all(),
        'name': request.session['active_forening'].name,
        'type': request.session['active_forening'].type,
        'group_type': request.session['active_forening'].group_type,
        'post_address': request.session['active_forening'].post_address,
        'visit_address': request.session['active_forening'].visit_address,
        'zipcode': zipcode.zipcode if zipcode is not None else '',
        'counties': request.session['active_forening'].counties.all(),
        'choose_contact': choose_contact,
        'contact_person': contact_person,
        'contact_person_name': contact_person_name,
        'phone': phone,
        'email': email,
        'organization_no': request.session['active_forening'].organization_no,
        'gmap_url': request.session['active_forening'].gmap_url,
        'facebook_url': request.session['active_forening'].facebook_url,
    })

    create_form = ForeningDataForm(request.user, prefix='create', initial={
        'zipcode': '',
    })

    context.update({
        'edit_form': edit_form,
        'create_form': create_form,
        'edit_form_zipcode_area': edit_form_zipcode_area,
    })

    if request.method == 'GET':
        return render(request, 'common/admin/forening/index.html', context)

    elif request.method == 'POST':

        if request.POST.get('form') == 'edit':
            edit_form = ExistingForeningDataForm(request.user, request.POST, prefix='edit')
            if edit_form.is_valid():
                forening = edit_form.cleaned_data['forening']
                forening.parents = edit_form.cleaned_data['parents']
                forening.name = edit_form.cleaned_data['name']
                forening.type = edit_form.cleaned_data['type']
                if forening.type == 'turgruppe':
                    forening.group_type = edit_form.cleaned_data['group_type']
                else:
                    forening.group_type = ''
                forening.post_address = edit_form.cleaned_data['post_address']
                forening.visit_address = edit_form.cleaned_data['visit_address']
                forening.zipcode = edit_form.cleaned_data['zipcode']
                forening.counties = edit_form.cleaned_data['counties']

                if edit_form.cleaned_data['choose_contact'] == 'person':
                    if edit_form.cleaned_data['contact_person'] is not None:
                        forening.contact_person = edit_form.cleaned_data['contact_person']
                        forening.contact_person_name = ''
                    else:
                        forening.contact_person = None
                        forening.contact_person_name = edit_form.cleaned_data['contact_person_name']
                else:
                    forening.contact_person = None
                    forening.contact_person_name = ''

                forening.phone = edit_form.cleaned_data['phone']
                forening.email = edit_form.cleaned_data['email']

                forening.organization_no = edit_form.cleaned_data['organization_no']
                forening.gmap_url = edit_form.cleaned_data['gmap_url']
                forening.facebook_url = edit_form.cleaned_data['facebook_url']
                forening.save()
                messages.info(request, 'forening_save_success')
                # Not sure why "request.session.modified = True" doesn't work here, so just update the var
                request.session['active_forening'] = forening
                cache.delete('foreninger.full_list')
                return redirect('admin.forening.views.index')
            else:
                context.update({'edit_form': edit_form})
                return render(request, 'common/admin/forening/index.html', context)

        elif request.POST.get('form') == 'create':
            create_form = ForeningDataForm(request.user, request.POST, prefix='create')
            if create_form.is_valid():
                forening = Forening()
                forening.name = create_form.cleaned_data['name']
                forening.type = create_form.cleaned_data['type']
                if forening.type == 'turgruppe':
                    forening.group_type = create_form.cleaned_data['group_type']
                else:
                    forening.group_type = ''
                forening.post_address = create_form.cleaned_data['post_address']
                forening.visit_address = create_form.cleaned_data['visit_address']
                forening.zipcode = create_form.cleaned_data['zipcode']

                if create_form.cleaned_data['choose_contact'] == 'person':
                    if create_form.cleaned_data['contact_person'] is not None:
                        forening.contact_person = create_form.cleaned_data['contact_person']
                        forening.contact_person_name = ''
                    else:
                        forening.contact_person = None
                        forening.contact_person_name = create_form.cleaned_data['contact_person_name']
                else:
                    forening.contact_person = None
                    forening.contact_person_name = ''

                forening.phone = create_form.cleaned_data['phone']
                forening.email = create_form.cleaned_data['email']

                forening.organization_no = create_form.cleaned_data['organization_no']
                forening.gmap_url = create_form.cleaned_data['gmap_url']
                forening.facebook_url = create_form.cleaned_data['facebook_url']
                forening.save()

                # Set M2M-fields after the initial db-save
                forening.parents = create_form.cleaned_data['parents']
                forening.counties = create_form.cleaned_data['counties']

                # Add the current user as admin on the new forening
                role = ForeningRole(
                    user=request.user,
                    forening=forening,
                    role='admin',
                )
                role.save()

                messages.info(request, 'forening_create_success')
                request.session['active_forening'] = forening
                cache.delete('foreninger.full_list')
                # Since GET url == POST url, we need to specifically set the tab hashtag we want, or the existing
                # one (create) will be kept
                return redirect('%s#metadata' % reverse('admin.forening.views.index'))
            else:
                context.update({'create_form': create_form})
                return render(request, 'common/admin/forening/index.html', context)

        else:
            return redirect('admin.forening.views.index')

def contact_person_search(request):
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
        'results': render_to_string('common/admin/forening/contact_person_search_results.html', context),
        'max_hits_exceeded': len(users) > MAX_HITS or len(actors) > MAX_HITS
    }))

def users_access_search(request):
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
        'results': render_to_string('common/admin/forening/users_access_search_results.html', context),
        'max_hits_exceeded': len(users) > MAX_HITS or len(actors) > MAX_HITS
    }))

def users_give_access(request, user, wanted_role):
    if wanted_role not in [role[0] for role in ForeningRole.ROLE_CHOICES]:
        raise PermissionDenied

    # Verify that the user has the same access that they're giving
    passed = False
    for forening in request.user.all_foreninger():
        if forening == request.session['active_forening']:
            if wanted_role == 'admin' and forening.role == 'user':
                raise PermissionDenied
            else:
                passed = True
    if not passed:
        raise PermissionDenied

    other_user = User.get_users(include_pending=True).get(id=user)
    if other_user.has_perm('sherpa_admin'):
        messages.info(request, 'user_is_sherpa_admin')
        return redirect('%s#brukere' % reverse('admin.forening.views.index'))

    # Adding the sherpa permission, if missing, is implicit - and informed about client-side
    if not other_user.has_perm('sherpa'):
        p = Permission.objects.get(name='sherpa')
        other_user.permissions.add(p)

    for forening in other_user.all_foreninger():
        if forening == request.session['active_forening']:
            # The user already has access to this forening
            print("Well, %s // %s" % (forening.role, wanted_role))
            if forening.role == 'user' and wanted_role == 'admin':
                # But it's a user role and we want admin! Update it.
                forening_role = ForeningRole.objects.get(user=other_user, forening=forening)
                forening_role.role = 'admin'
                forening_role.save()
                messages.info(request, 'permission_created')
            elif forening.role == 'admin' and wanted_role == 'user':
                # We want user access, but they have admin. Chcek if it's an explicit relationship:
                try:
                    forening_role = ForeningRole.objects.get(user=other_user, forening=forening)
                    forening_role.role = 'user'
                    forening_role.save()
                    messages.info(request, 'permission_created')
                except ForeningRole.DoesNotExist:
                    # No explicit relationship, so the user must have admin access to a parent
                    messages.info(request, 'user_has_admin_in_parent')
            else:
                # In this case, forening.role should equal wanted_role, so just inform the user that all is in order
                messages.info(request, 'equal_permission_already_exists')
            cache.delete('user.%s.all_foreninger' % other_user.id)
            return redirect('%s#brukere' % reverse('admin.forening.views.index'))

    # If we reach this code path, this is a new relationship - create it
    forening_role = ForeningRole(
        user=other_user,
        forening=request.session['active_forening'],
        role=wanted_role,
    )
    forening_role.save()
    messages.info(request, 'permission_created')
    cache.delete('user.%s.all_foreninger' % other_user.id)
    return redirect('%s#brukere' % reverse('admin.forening.views.index'))


