# encoding: utf-8
import json
from StringIO import StringIO
from hashlib import sha1
import re

from django.shortcuts import render, redirect
from django.conf import settings

import requests
import boto
from PIL import Image

from admin.models import Campaign, CampaignText
from core.models import Site
from core.util import s3_bucket

def index(request, site):
    active_site = Site.objects.get(id=site)
    campaigns = Campaign.on(active_site).all()
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

    post_data = json.loads(request.POST['campaign'])
    crop = post_data['image_crop']

    # Download the supplied image
    r = requests.get(post_data['image_original'])
    image = Image.open(StringIO(r.content))

    # Crop and resize the original image
    width_ratio = float(image.size[0]) / crop['width']
    height_ratio = float(image.size[1]) / crop['height']

    box = (
        int(crop['selection']['x'] * width_ratio),
        int(crop['selection']['y'] * height_ratio),
        int(crop['selection']['x2'] * width_ratio),
        int(crop['selection']['y2'] * height_ratio),
    )

    campaign_image = image.crop(box).resize((940, 480))
    campaign_image_file = StringIO()
    campaign_image.save(campaign_image_file, "JPEG")
    campaign_image_file = campaign_image_file.getvalue()

    # Retrieve or create the campaign object
    try:
        campaign = Campaign.objects.get(id=request.POST['existing_campaign'])

        # This is an existing campaign
        generate_ga_event_label = False
        campaign.delete_cropped_image() # delete the previous cropped image
    except (ValueError, Campaign.DoesNotExist):
        campaign = Campaign()
        generate_ga_event_label = True

    # Save the prepared image to S3
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(s3_bucket())

    hash_ = sha1(campaign_image_file).hexdigest()
    key = bucket.new_key(Campaign.cropped_image_key(hash_))
    key.content_type = u'image/jpeg'.encode('utf-8') # Give boto an explicitly encoded str, not unicode
    key.set_contents_from_string(campaign_image_file, policy='public-read')

    # And finally save the rest of the campaign data
    campaign.title = post_data['title']
    campaign.image_original = post_data['image_original']
    campaign.image_cropped_hash = hash_
    campaign.image_crop = json.dumps(crop)
    campaign.photographer = request.POST['photographer']
    if campaign.photographer != '':
        campaign.photographer_alignment = post_data['photographer_alignment']
        campaign.photographer_color = post_data['photographer_color']
    campaign.button_enabled = post_data['button_enabled']
    campaign.button_label = post_data['button_label']
    campaign.button_anchor = post_data['button_anchor']
    campaign.button_large = post_data['button_large']
    campaign.button_position = json.dumps(post_data['button_position'])
    campaign.site = active_site
    campaign.save()

    # Set fields that depend on the DB id being set
    campaign.utm_campaign = '%s-%s' % (re.sub('\s', '_', campaign.title), campaign.id)
    if generate_ga_event_label:
        campaign.ga_event_label = campaign.generate_ga_event_label()
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
