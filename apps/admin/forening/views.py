# encoding: utf-8
from django.shortcuts import render, redirect
from django.contrib import messages

from foreninger.models import Forening
from .forms import ForeningDataForm

def index(request, forening):
    if request.method == 'GET':

        form = ForeningDataForm(initial={
            'name': request.session['active_forening'].name,
        })
        context = {'form': form}
        return render(request, 'common/admin/forening/index.html', context)

    elif request.method == 'POST':

        form = ForeningDataForm(request.POST)
        if form.is_valid():
            forening = Forening.objects.get(id=forening)
            forening.name = form.cleaned_data['name']
            forening.save()
            messages.info(request, 'forening_save_success')
            # Not sure why "request.session.modified = True" doesn't work here, so just update the var
            request.session['active_forening'] = forening
            return redirect('admin.forening.views.index', forening.id)
        else:
            context = {'form': form}
            return render(request, 'common/admin/forening/index.html', context)
