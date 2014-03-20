# encoding: utf-8
from django.shortcuts import render, redirect
from django.contrib import messages

from foreninger.models import Forening
from .forms import ForeningDataForm

def index(request, forening):
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
        })
        context = {
            'form': form,
            'form_zipcode_area': form_zipcode_area,
        }
        return render(request, 'common/admin/forening/index.html', context)

    elif request.method == 'POST':

        form = ForeningDataForm(request.POST)
        if form.is_valid():
            forening = Forening.objects.get(id=forening)
            forening.name = form.cleaned_data['name']
            forening.type = form.cleaned_data['type']
            forening.post_address = form.cleaned_data['post_address']
            forening.visit_address = form.cleaned_data['visit_address']
            forening.zipcode = form.cleaned_data['zipcode']
            forening.counties = form.cleaned_data['counties']
            forening.save()
            messages.info(request, 'forening_save_success')
            # Not sure why "request.session.modified = True" doesn't work here, so just update the var
            request.session['active_forening'] = forening
            return redirect('admin.forening.views.index', forening.id)
        else:
            context = {'form': form}
            return render(request, 'common/admin/forening/index.html', context)
