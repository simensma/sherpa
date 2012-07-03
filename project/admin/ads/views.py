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
def create_ad(request):
    if not request.FILES.has_key('ad'):
        # TODO error handling
        return HttpResponseRedirect(reverse('admin.ads.views.list'))

    hash, extension, content_type = upload(request.FILES['ad'])
    fallback_hash = None
    fallback_extension = None
    fallback_content_type = None

    if request.FILES.has_key('ad_fallback'):
        fallback_hash, fallback_extension, fallback_content_type = upload(request.FILES['ad_fallback'])
    width = None if request.POST['width'] == '' else request.POST['width'].strip()
    height = None if request.POST['height'] == '' else request.POST['height'].strip()

    ad = Ad(name=request.POST['name'].strip(), extension=extension,
        destination=request.POST['destination'].strip(), sha1_hash=hash,
        width=width, height=height, content_type=content_type, fallback_extension=fallback_extension,
        fallback_sha1_hash=fallback_hash, fallback_content_type=fallback_content_type)
    ad.save()
    return HttpResponseRedirect(reverse('admin.ads.views.list'))

@login_required
def update_ad(request):
    ad = Ad.objects.get(id=request.POST['id'])
    ad.name = request.POST['name']
    ad.destination = request.POST['destination']
    if ad.width != None: ad.width = request.POST['width']
    if ad.height != None: ad.height = request.POST['height']
    if request.FILES.has_key('ad'):
        ad.delete_file()
        ad.sha1_hash, ad.extension, ad.content_type = upload(request.FILES['ad'])
    if request.FILES.has_key('ad_fallback'):
        ad.delete_fallback_file()
        ad.fallback_sha1_hash, ad.fallback_extension, ad.fallback_content_type = upload(request.FILES['ad_fallback'])
    ad.save()
    return HttpResponseRedirect(reverse('admin.ads.views.list'))

@login_required
def create_placement(request):
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
def update_placement(request):
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

def upload(file):
    # Whoa! This S3-lib doesn't support streaming, so we'll have to read the whole
    # file into memory instead of streaming it to AWS. This might need to be
    # optimized at some point.
    data = file.read()

    # Calculate the sha1-hash and file extension
    sha1 = hashlib.sha1()
    sha1.update(data)
    hash = sha1.hexdigest()
    extension = file.name.split(".")[-1].lower()

    # Upload to AWS
    conn = S3.AWSAuthConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    conn.put(settings.AWS_BUCKET, "%s%s.%s"
        % (settings.AWS_ADS_PREFIX, hash, extension), S3.S3Object(data),
        {'x-amz-acl': 'public-read', 'Content-Type': file.content_type}
    )

    return (hash, extension, file.content_type)
