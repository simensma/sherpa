# encoding: utf-8
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

from datetime import datetime
import json
import hashlib
from lib import S3

from page.models import Ad, AdPlacement

@login_required
def list(request):
    ads = Ad.objects.all()
    placements = AdPlacement.objects.all().order_by('start_date', 'end_date')
    context = {'ads': ads, 'placements': placements}
    return render(request, 'admin/ads/list.html', context)

@login_required
def upload(request):
    if not request.FILES.has_key('ad'):
        # TODO error handling
        return HttpResponseRedirect(reverse('admin.ads.views.list'))

    file = request.FILES['ad']
    # Whoa! This S3-lib doesn't support streaming, so we'll have to read the whole
    # file into memory instead of streaming it to AWS. This might need to be
    # optimized at some point.
    data = file.read()

    # Calculate the sha1-hash
    sha1 = hashlib.sha1()
    sha1.update(data)
    hash = sha1.hexdigest()

    # File extension and image type
    ext = file.name.split(".")[-1].lower()

    width = None if request.POST['width'] == '' else request.POST['width']
    height = None if request.POST['height'] == '' else request.POST['height']

    conn = S3.AWSAuthConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    conn.put(settings.AWS_BUCKET, "%s%s.%s"
        % (settings.AWS_ADS_PREFIX, hash, ext), S3.S3Object(data),
        {'x-amz-acl': 'public-read', 'Content-Type': file.content_type}
    )

    ad = Ad(name=request.POST['name'], extension=ext, destination=request.POST['destination'],
        sha1_hash=hash, width=width, height=height, content_type=file.content_type)
    ad.save()
    return HttpResponseRedirect(reverse('admin.ads.views.list'))
