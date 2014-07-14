# encoding: utf-8
from django.shortcuts import render, redirect

from admin.models import Campaign, CampaignText
from core.models import Site

import json

def index(request, site):
    active_site = Site.objects.get(id=site)
    campaigns = Campaign.objects.all()
    context = {
        'active_site': active_site,
        'campaigns': campaigns,
    }
    return render(request, 'common/admin/sites/campaigns/index.html', context)

def edit(request, site):
    active_site = Site.objects.get(id=site)
    context = {
        'active_site': active_site,
        'font_sizes': range(20, 77),
    }
    return render(request, 'common/admin/sites/campaigns/edit.html', context)

def save(request, site):
    active_site = Site.objects.get(id=site)
    post_data = json.loads(request.POST['campaign'])
    campaign = Campaign(
        title=post_data['title'],
        image_url=post_data['image_url'],
        image_crop=json.dumps(post_data['image_crop']),
        button_enabled=post_data['button_enabled'],
        button_label=post_data['button_label'],
        button_anchor=post_data['button_anchor'],
        button_large=post_data['button_large'],
        button_position=json.dumps(post_data['button_position']),
        site=active_site,
    )
    campaign.save()
    for post_text in post_data['text']:
        campaign_text = CampaignText(
            campaign=campaign,
            content=post_text['content'],
            style=json.dumps(post_text['style']),
        )
        campaign_text.save()
    return redirect('admin.sites.campaigns.views.index', active_site.id)
