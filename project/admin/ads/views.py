# encoding: utf-8
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from datetime import datetime
import json

from page.models import Ad, AdPlacement

@login_required
def list(request):
    ads = Ad.objects.all()
    placements = AdPlacement.objects.all()
    context = {'ads': ads, 'placements': placements}
    return render(request, 'admin/ads/list.html', context)
