# encoding: utf-8
from django.shortcuts import render

from admin.models import Campaign

def index(request):
    campaigns = Campaign.objects.all()
    context = {'campaigns': campaigns}
    return render(request, 'common/admin/campaigns/index.html', context)
