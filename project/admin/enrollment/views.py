# encoding: utf-8
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    context = {}
    return render(request, 'admin/enrollment/index.html', context)
