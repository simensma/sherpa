# encoding: utf-8
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages

from datetime import datetime
import hashlib
import simples3

from admin.ads.util import parse_adform_script_destination
from page.models import Ad, AdPlacement

def list(request):
    ads = Ad.objects.all().order_by('name')
    time_placements = AdPlacement.objects.filter(start_date__isnull=False).order_by('start_date', 'end_date')
    view_placements = AdPlacement.objects.filter(view_limit__isnull=False).order_by('views')
    context = {'ads': ads, 'time_placements': time_placements, 'view_placements': view_placements}
    return render(request, 'common/admin/ads/list.html', context)

def create_ad(request):

    if request.POST['type'] == 'file':

        if not 'ad' in request.FILES:
            return redirect('admin.ads.views.list')

        hash, extension, content_type = upload(request.FILES['ad'])
        fallback_hash = None
        fallback_extension = None
        fallback_content_type = None

        if 'ad_fallback' in request.FILES:
            fallback_hash, fallback_extension, fallback_content_type = upload(request.FILES['ad_fallback'])
        width = None if request.POST['width'] == '' else request.POST['width'].strip()
        height = None if request.POST['height'] == '' else request.POST['height'].strip()

        ad = Ad(
            name=request.POST['name'].strip(),
            extension=extension,
            destination=request.POST['destination'].strip(),
            viewcounter=request.POST['viewcounter'].strip(),
            sha1_hash=hash,
            width=width,
            height=height,
            content_type=content_type,
            fallback_extension=fallback_extension,
            fallback_sha1_hash=fallback_hash,
            fallback_content_type=fallback_content_type
        )
        ad.save()

    elif request.POST['type'] == 'adform-script':

        try:
            script = request.POST['script'].strip()
            destination = parse_adform_script_destination(script)

            ad = Ad(
                name=request.POST['name'].strip(),
                extension='',
                destination=destination,
                viewcounter=request.POST['viewcounter'].strip(),
                sha1_hash='',
                width=None,
                height=None,
                content_script=script,
                content_type=Ad.ADFORM_SCRIPT_CONTENT_TYPE,
                fallback_extension=None,
                fallback_sha1_hash=None,
                fallback_content_type=None
            )
            ad.save()
        except IndexError:
            messages.error(request, 'unparseable_script')

    return redirect('admin.ads.views.list')

def update_ad(request):
    try:
        ad = Ad.objects.get(id=request.POST['id'])
        ad.name = request.POST['name']
        ad.viewcounter = request.POST['viewcounter']

        if not ad.is_adform_script():
            ad.destination = request.POST['destination'].strip()
            if ad.width is not None: ad.width = request.POST['width']
            if ad.height is not None: ad.height = request.POST['height']
            if 'ad' in request.FILES:
                ad.delete_file()
                ad.sha1_hash, ad.extension, ad.content_type = upload(request.FILES['ad'])
            if 'ad_fallback' in request.FILES:
                ad.delete_fallback_file()
                ad.fallback_sha1_hash, ad.fallback_extension, ad.fallback_content_type = upload(request.FILES['ad_fallback'])
        else:
            script = request.POST['script'].strip()
            ad.destination = parse_adform_script_destination(script)
            ad.content_script = script

        ad.save()
    except IndexError:
        messages.error(request, 'unparseable_script')

    return redirect('admin.ads.views.list')

def create_placement(request):
    try:
        ad = Ad.objects.get(id=request.POST['ad'])
        if request.POST['adplacement_type'] == 'time':
            start_date = datetime.strptime(request.POST['start_date'], "%d.%m.%Y")
            end_date = datetime.strptime(request.POST['end_date'], "%d.%m.%Y")
            view_limit = None
        else:
            start_date = None
            end_date = None
            view_limit = request.POST['view_limit']
        ap = AdPlacement(ad=ad, start_date=start_date, end_date=end_date, view_limit=view_limit)
        ap.save()
    except ValueError:
        messages.error(request, 'invalid_date')
    return redirect('admin.ads.views.list')

def update_placement(request):
    try:
        placement = AdPlacement.objects.get(id=request.POST['id'])
        placement.ad = Ad.objects.get(id=request.POST['ad'])
        if placement.start_date is not None:
            placement.start_date = datetime.strptime(request.POST['start_date'], "%d.%m.%Y")
            placement.end_date = datetime.strptime(request.POST['end_date'], "%d.%m.%Y")
        else:
            placement.view_limit = request.POST['view_limit']
        placement.save()
    except ValueError:
        messages.error(request, 'invalid_date')
    return redirect('admin.ads.views.list')

def upload(file):
    # TODO: Consider streaming the file instead of reading everything into memory first.
    # See simples3/htstream.py
    data = file.read()

    # Calculate the sha1-hash and file extension
    sha1 = hashlib.sha1()
    sha1.update(data)
    hash = sha1.hexdigest()
    extension = file.name.split(".")[-1].lower()

    # Upload to AWS
    s3 = simples3.S3Bucket(settings.AWS_BUCKET, settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY, 'https://%s' % settings.AWS_BUCKET)
    s3.put("%s%s.%s" % (settings.AWS_ADS_PREFIX, hash, extension),
        data, acl='public-read', mimetype=file.content_type)

    return (hash, extension, file.content_type)
