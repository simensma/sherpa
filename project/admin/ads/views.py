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

invalid_date = 'ugyldig-datoformat'
added = 'annonse-lagt-til'

@login_required
def list(request):
    ads = Ad.objects.all().order_by('name')
    pages = []
    for page in AdPlacement.PLACEMENTS:
        placements = AdPlacement.objects.filter(placement=page[0]).order_by('start_date', 'end_date')
        pages.append({'page': page, 'placements': placements})
    context = {'ads': ads, 'pages': pages,
        'invalid_date': request.GET.has_key(invalid_date),
        'added': request.GET.has_key(added)}
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

    width = None if request.POST['width'] == '' else request.POST['width'].strip()
    height = None if request.POST['height'] == '' else request.POST['height'].strip()

    conn = S3.AWSAuthConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    conn.put(settings.AWS_BUCKET, "%s%s.%s"
        % (settings.AWS_ADS_PREFIX, hash, ext), S3.S3Object(data),
        {'x-amz-acl': 'public-read', 'Content-Type': file.content_type}
    )

    ad = Ad(name=request.POST['name'].strip(), extension=ext, destination=request.POST['destination'].strip(),
        sha1_hash=hash, width=width, height=height, content_type=file.content_type)
    ad.save()
    return HttpResponseRedirect(reverse('admin.ads.views.list'))

@login_required
def place(request):
    try:
        ad = Ad.objects.get(id=request.POST['ad'])
        start_date = datetime.strptime(request.POST['start_date'], "%d.%m.%Y")
        end_date = datetime.strptime(request.POST['end_date'], "%d.%m.%Y")
        ap = AdPlacement(ad=ad, start_date=start_date, end_date=end_date,
            placement=request.POST['placement'])
        ap.save()
    except ValueError:
        return HttpResponseRedirect("%s?%s" % (reverse('admin.ads.views.list'), invalid_date))
    return HttpResponseRedirect("%s?%s" % (reverse('admin.ads.views.list'), added))

@login_required
def replace(request):
    try:
        placement = AdPlacement.objects.get(id=request.POST['id'])
        placement.ad = Ad.objects.get(id=request.POST['ad'])
        placement.start_date = datetime.strptime(request.POST['start_date'], "%d.%m.%Y")
        placement.end_date = datetime.strptime(request.POST['end_date'], "%d.%m.%Y")
        placement.placement = request.POST['placement']
        placement.save()
    except ValueError:
        return HttpResponseRedirect("%s?%s" % (reverse('admin.ads.views.list'), invalid_date))
    return HttpResponseRedirect("%s?%s" % (reverse('admin.ads.views.list'), added))
