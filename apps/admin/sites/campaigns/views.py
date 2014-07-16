# encoding: utf-8
from django.shortcuts import render, redirect

import json

from admin.models import Campaign, CampaignText
from core.models import Site

def index(request, site):
    active_site = Site.objects.get(id=site)
    campaigns = Campaign.objects.all()
    context = {
        'active_site': active_site,
        'campaigns': campaigns,
    }
    return render(request, 'common/admin/sites/campaigns/index.html', context)

def edit(request, site, campaign):
    active_site = Site.objects.get(id=site)
    context = {
        'active_site': active_site,
        'font_sizes': range(16, 77),
    }
    if campaign is not None:
        context['campaign'] = Campaign.objects.get(id=campaign)
    return render(request, 'common/admin/sites/campaigns/edit.html', context)

def save(request, site):
    active_site = Site.objects.get(id=site)

    try:
        campaign = Campaign.objects.get(id=request.POST['existing_campaign'])
    except (ValueError, Campaign.DoesNotExist):
        campaign = Campaign()

    post_data = json.loads(request.POST['campaign'])
    campaign.title = post_data['title']
    campaign.image_url = post_data['image_url']
    campaign.image_crop = json.dumps(post_data['image_crop'])
    campaign.button_enabled = post_data['button_enabled']
    campaign.button_label = post_data['button_label']
    campaign.button_anchor = post_data['button_anchor']
    campaign.button_large = post_data['button_large']
    campaign.button_position = json.dumps(post_data['button_position'])
    campaign.site = active_site
    campaign.save()

    campaign.text.all().delete()

    for post_text in post_data['text']:
        campaign_text = CampaignText(
            campaign=campaign,
            content=post_text['content'],
            style=json.dumps(post_text['style']),
        )
        campaign_text.save()
    return redirect('admin.sites.campaigns.views.index', active_site.id)
