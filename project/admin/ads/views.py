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
    placements = AdPlacement.objects.all()
    context = {'ads': ads, 'placements': placements}
    return render(request, 'admin/ads/list.html', context)

@login_required
def upload(request):
    if len(request.FILES.getlist('files')) == 0:
        return render(request, 'admin/ads/iframe.html', {'result': 'no_files'})
    for file in request.FILES.getlist('files'):
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

        conn = S3.AWSAuthConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        conn.put(settings.AWS_BUCKET, "%s%s.%s"
            % (settings.AWS_ADS_PREFIX, hash, ext), S3.S3Object(data),
            {'x-amz-acl': 'public-read', 'Content-Type': file.content_type}
        )

        ad = Ad(name=request.POST['name'], extension=ext, destination=request.POST['destination'],
            sha1_hash=hash, content_type=file.content_type)
        ad.save()
    return render(request, 'admin/images/iframe.html', {'result': 'success'})
