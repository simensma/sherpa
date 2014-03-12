# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.conf import settings

import json
import sys
import logging
from cStringIO import StringIO
from hashlib import sha1
from datetime import datetime

import boto
from PIL import Image as pil

from admin.models import Image, Fotokonkurranse
from core.models import Tag
from admin.images.util import generate_unique_random_image_key, get_exif_tags, create_thumb
from core import xmp, validator

logger = logging.getLogger('sherpa')

def default(request):
    context = {
        'destination_album_exists': Fotokonkurranse.objects.get().album is not None,
        'now': datetime.now(),
    }
    return render(request, 'main/fotokonkurranse/default.html', context)

def upload(request):
    try:
        image_file = request.FILES['file']
    except KeyError:
        raise PermissionDenied

    if not validator.name(request.POST.get('name', '')):
        raise PermissionDenied

    if not validator.phone(request.POST.get('phone', '')):
        raise PermissionDenied

    if not validator.email(request.POST.get('email', '')):
        raise PermissionDenied

    if len(request.POST.get('description', '').strip()) == 0:
        raise PermissionDenied

    post_name = request.POST['name'].strip()
    post_phone = request.POST['phone'].strip()
    post_email = request.POST['email'].strip()
    post_description = request.POST['description'].strip()

    try:
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_BUCKET)

        image_key = generate_unique_random_image_key()
        data = image_file.read()
        ext = image_file.name.split(".")[-1].lower()
        pil_image = pil.open(StringIO(data))
        exif_json = json.dumps(get_exif_tags(pil_image))
        image_file_tags = xmp.find_keywords(data)
        thumbs = [{'size': size, 'data': create_thumb(pil_image, ext, size)} for size in settings.THUMB_SIZES]

        key = boto.s3.key.Key(bucket, '%s%s.%s' % (settings.AWS_IMAGEGALLERY_PREFIX, image_key, ext))
        key.content_type = image_file.content_type
        key.set_contents_from_string(data)
        key.set_acl('public-read')

        for thumb in thumbs:
            key = boto.s3.key.Key(bucket, '%s%s-%s.%s' % (settings.AWS_IMAGEGALLERY_PREFIX, image_key, thumb['size'], ext))
            key.content_type = image_file.content_type
            key.set_contents_from_string(thumb['data'])
            key.set_acl('public-read')

        destination_album = Fotokonkurranse.objects.get().album
        licence_text = "Kan brukes i DNTs egne kommunikasjonskanaler som magasiner, nettsider og sosiale medier, i PR og for bruk av DNTs sponsorer."

        image = Image(
            key=image_key,
            extension=ext,
            hash=sha1(data).hexdigest(),
            description=post_description,
            album=destination_album,
            photographer=post_name,
            credits="%s / DNTs fotokonkurranse" % post_name,
            licence="%s Kontakt: %s (%s / %s)" % (licence_text, post_name, post_phone, post_email),
            exif=exif_json,
            uploader=request.user if not request.user.is_anonymous() else None,
            width=pil_image.size[0],
            height=pil_image.size[1])
        image.save()

        for tag in [tag.lower() for tag in image_file_tags]:
            obj, created = Tag.objects.get_or_create(name=tag)
            image.tags.add(obj)

        return HttpResponse(json.dumps({
            'files': [{
                'name': image_file.name,
                'size': image_file.size,
                'url': '',
                'thumbnailUrl': '',
                'deleteUrl': '',
                'deleteType': '',
            }]
        }))
    except Exception as e:
        logger.error(u"Feil ved opplasting av bilde til fotokonkurranse",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        return HttpResponseBadRequest(json.dumps({
            'files': [{
                'name': image_file.name,
                'size': image_file.size,
                'error': "Exception ved bildeopplasting: %s" % e,
            }]
        }))
