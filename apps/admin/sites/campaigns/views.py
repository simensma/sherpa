# encoding: utf-8
from django.shortcuts import render

from admin.models import Campaign
from core.models import Site

def index(request, site):
    active_site = Site.objects.get(id=site)
    campaigns = Campaign.objects.all()
    context = {
        'active_site': active_site,
        'campaigns': campaigns,
    }
    return render(request, 'common/admin/sites/campaigns/index.html', context)

def new(request, site):
    active_site = Site.objects.get(id=site)
    context = {
        'active_site': active_site,
        'font_sizes': range(20, 77),
    }
    return render(request, 'common/admin/sites/campaigns/new.html', context)
