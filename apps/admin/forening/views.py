# encoding: utf-8
from django.shortcuts import render, redirect
from django.contrib import messages

from foreninger.models import Forening
from .forms import ForeningDataForm
from user.models import User

def index(request, forening):
    forening_users = list(User.objects.filter(foreninger=request.session['active_forening']))

    forening_users_by_parent = []
    forening = request.session['active_forening']
    while forening.parent is not None:
        forening = forening.parent
        for user in User.objects.filter(foreninger=forening):
            forening_users_by_parent.append(user)

    context = {
        'forening_users': forening_users,
        'forening_users_by_parent': forening_users_by_parent,
    }

    if request.method == 'GET':

        zipcode = request.session['active_forening'].zipcode
        form_zipcode_area = zipcode.area if zipcode is not None else ''

        form = ForeningDataForm(initial={
            'name': request.session['active_forening'].name,
            'type': request.session['active_forening'].type,
            'post_address': request.session['active_forening'].post_address,
            'visit_address': request.session['active_forening'].visit_address,
            'zipcode': zipcode.zipcode if zipcode is not None else '',
            'counties': request.session['active_forening'].counties.all(),
            'phone': request.session['active_forening'].phone,
            'email': request.session['active_forening'].email,
            'organization_no': request.session['active_forening'].organization_no,
            'gmap_url': request.session['active_forening'].gmap_url,
            'facebook_url': request.session['active_forening'].facebook_url,
        })
        context.update({
            'form': form,
            'form_zipcode_area': form_zipcode_area,
        })
        return render(request, 'common/admin/forening/index.html', context)

    elif request.method == 'POST':

        form = ForeningDataForm(request.POST)
        if form.is_valid():
            forening = Forening.objects.get(id=forening)
            forening.name = form.cleaned_data['name']
            forening.type = form.cleaned_data['type']
            if forening.type == 'turgruppe':
                forening.group_type = form.cleaned_data['group_type']
            else:
                forening.group_type = ''
            forening.post_address = form.cleaned_data['post_address']
            forening.visit_address = form.cleaned_data['visit_address']
            forening.zipcode = form.cleaned_data['zipcode']
            forening.counties = form.cleaned_data['counties']
            forening.phone = form.cleaned_data['phone']
            forening.email = form.cleaned_data['email']
            forening.organization_no = form.cleaned_data['organization_no']
            forening.gmap_url = form.cleaned_data['gmap_url']
            forening.facebook_url = form.cleaned_data['facebook_url']
            forening.save()
            messages.info(request, 'forening_save_success')
            # Not sure why "request.session.modified = True" doesn't work here, so just update the var
            request.session['active_forening'] = forening
            return redirect('admin.forening.views.index')
        else:
            context.update({'form': form})
            return render(request, 'common/admin/forening/index.html', context)
