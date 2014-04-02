# encoding: utf-8
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings

from foreninger.models import Forening
from .forms import ForeningDataForm, ExistingForeningDataForm
from user.models import User, ForeningRole
from focus.models import Actor

def index(request):
    forening_users = list(User.objects.filter(foreninger=request.session['active_forening']))

    forening_users_by_parent = []
    active_forening = request.session['active_forening']
    while active_forening.parent is not None:
        active_forening = active_forening.parent
        for user in User.objects.filter(foreninger=active_forening):
            forening_users_by_parent.append(user)

    # Prefetch and cache the actors
    memberids = [u.memberid for u in (forening_users + forening_users_by_parent)]
    for actor in Actor.objects.filter(memberid__in=memberids):
        cache.set('actor.%s' % actor.memberid, actor, settings.FOCUS_MEMBER_CACHE_PERIOD)

    # Safe to iterate without having n+1 issues
    forening_users = sorted(forening_users, key=lambda u: u.get_full_name())
    forening_users_by_parent = sorted(forening_users_by_parent, key=lambda u: u.get_full_name())

    # The parent choices are tricky to define in the forms API, so do it here
    all_sorted = request.user.all_foreninger_sorted()
    parent_choices = {
        'foreninger': all_sorted['foreninger'],
        'turlag': all_sorted['turlag'],
    }

    context = {
        'forening_users': forening_users,
        'forening_users_by_parent': forening_users_by_parent,
        'parent_choices': parent_choices,
    }

    zipcode = request.session['active_forening'].zipcode
    edit_form_zipcode_area = zipcode.area if zipcode is not None else ''

    edit_form = ExistingForeningDataForm(request.user, prefix='edit', initial={
        'forening': request.session['active_forening'].id,
        'parent': request.session['active_forening'].parent,
        'name': request.session['active_forening'].name,
        'type': request.session['active_forening'].type,
        'post_address': request.session['active_forening'].post_address,
        'visit_address': request.session['active_forening'].visit_address,
        'zipcode': zipcode.zipcode if zipcode is not None else '',
        'counties': request.session['active_forening'].counties.all(),
        'contact_person': request.session['active_forening'].contact_person,
        'contact_person_name': request.session['active_forening'].contact_person_name,
        'phone': request.session['active_forening'].phone,
        'email': request.session['active_forening'].email,
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
                forening.parent = edit_form.cleaned_data['parent']
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

                if request.POST['edit-choose-contact'] == 'person':
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
                return redirect('admin.forening.views.index')
            else:
                context.update({'edit_form': edit_form})
                return render(request, 'common/admin/forening/index.html', context)

        elif request.POST.get('form') == 'create':
            create_form = ForeningDataForm(request.user, request.POST, prefix='create')
            if create_form.is_valid():
                forening = Forening()
                forening.parent = create_form.cleaned_data['parent']
                forening.name = create_form.cleaned_data['name']
                forening.type = create_form.cleaned_data['type']
                if forening.type == 'turgruppe':
                    forening.group_type = create_form.cleaned_data['group_type']
                else:
                    forening.group_type = ''
                forening.post_address = create_form.cleaned_data['post_address']
                forening.visit_address = create_form.cleaned_data['visit_address']
                forening.zipcode = create_form.cleaned_data['zipcode']
                forening.phone = create_form.cleaned_data['phone']
                forening.email = create_form.cleaned_data['email']
                forening.organization_no = create_form.cleaned_data['organization_no']
                forening.gmap_url = create_form.cleaned_data['gmap_url']
                forening.facebook_url = create_form.cleaned_data['facebook_url']
                forening.save()

                # Set M2M-fields after the initial db-save
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
                # Since GET url == POST url, we need to specifically set the tab hashtag we want, or the existing
                # one (create) will be kept
                return redirect('%s#metadata' % reverse('admin.forening.views.index'))
            else:
                context.update({'create_form': create_form})
                return render(request, 'common/admin/forening/index.html', context)

        else:
            return redirect('admin.forening.views.index')
