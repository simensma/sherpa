# encoding: utf-8
from cStringIO import StringIO
from hashlib import sha1
import json
import logging
import sys
import zipfile
import tempfile

from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render

import PIL.Image
import PIL.ExifTags
import boto
import pyexiv2

from core.models import Tag
from admin.models import Image, Album
from core import xmp
from core.util import s3_bucket

logger = logging.getLogger('sherpa')

def content_dialog(request):
    album = json.loads(request.POST['album'])
    if album == '':
        objects = parse_objects([], Album.objects.filter(parent=None).order_by('name'), [])
    else:
        current_album = Album.objects.get(id=album)
        objects = parse_objects(list_parents(current_album),
            Album.objects.filter(parent=album).order_by('name'),
            Image.objects.filter(album=album))

    context = RequestContext(request, {
        'parents': objects['parents'],
        'albums': objects['albums'],
        'albums_divided': divide_for_three_columns(objects['albums']),
        'images': objects['images'],
        'list_status': 'album' if album != '' else 'root_album'
        })
    return HttpResponse(json.dumps({'html': render_to_string('common/admin/images/util/image-archive-picker-content.html', context)}))

def mine_dialog(request):
    images = Image.objects.filter(uploader=request.user)

    context = RequestContext(request, {
        'images': images,
        'list_status': 'album'
        })
    return HttpResponse(json.dumps({'html': render_to_string('common/admin/images/util/image-archive-picker-content.html', context)}))

def search_dialog(request):
    query = json.loads(request.POST['query'])
    if len(query) < settings.IMAGE_SEARCH_LENGTH:
        albums = Album.objects.none()
        images = Image.objects.none()
    else:
        albums, images = full_archive_search(query)
    objects = parse_objects([], albums, images)
    context = RequestContext(request, {
        'parents': objects['parents'],
        'albums': objects['albums'],
        'albums_divided': divide_for_three_columns(objects['albums']),
        'images': objects['images'],
        'list_status': 'search',
        'search_query': query
        })
    return HttpResponse(json.dumps({'html': render_to_string('common/admin/images/util/image-archive-picker-content.html', context)}))

def image_upload_dialog(request):
    try:
        image = request.FILES['file']
    except KeyError:
        result = json.dumps({'status': 'no_files'})
        return render(request, 'common/admin/images/iframe.html', {'result': result})

    try:
        image = upload_image(
            image_data=image.read(),
            extension=image.name.split(".")[-1].lower(),
            description=request.POST['description'],
            album=None,
            photographer=request.POST['photographer'],
            credits=request.POST['credits'],
            licence=request.POST['licence'],
            content_type=image.content_type,
            tags=[tag.strip() for tag in request.POST['tags'].split(',') if tag.strip() != ''],
            uploader=request.user,
        )

        result = json.dumps({
            'status': 'success',
            'url': 'http://%s/%s%s.%s' % (s3_bucket(), settings.AWS_IMAGEGALLERY_PREFIX, image.key, image.extension),
        })
        return render(request, 'common/admin/images/iframe.html', {'result': result})
    except(IOError, KeyError):
        logger.warning(u"Kunne ikke parse opplastet bilde, antar at det er ugyldig bildefil",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        result = json.dumps({'status': 'parse_error'})
        return render(request, 'common/admin/images/iframe.html', {'result': result})
    except Exception:
        logger.error(u"Ukjent exception ved bildeopplasting",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        result = json.dumps({'status': 'unknown_exception'})
        return render(request, 'common/admin/images/iframe.html', {'result': result})


#
# Actual utilities
#

def upload_image(image_data, extension, description, album, photographer, credits, licence, content_type, tags, uploader):
    """Note that the provided file extension will be standardized and may change, so callers should take care to use
    the extension of the returned image object if needed further."""
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(s3_bucket())

    image_key = Image.generate_unique_random_key()
    pil_image = PIL.Image.open(StringIO(image_data))
    extension = standardize_extension(extension)

    # cannot write P mode as JPEG; see http://stackoverflow.com/q/21669657/302484
    if extension == 'jpeg' and pil_image.mode == 'P':
        pil_image = pil_image.convert('RGB')

    exif_json = json.dumps(get_exif_tags(pil_image))
    image_file_tags = xmp.find_keywords(image_data)
    thumbs = [{'size': size, 'data': create_thumb(pil_image, extension, size)} for size in settings.THUMB_SIZES]

    key = bucket.new_key("%s%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, image_key, extension))
    key.content_type = content_type
    key.set_contents_from_string(image_data, policy='public-read')

    for thumb in thumbs:
        key = bucket.new_key("%s%s-%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, image_key, thumb['size'], extension))
        key.content_type = content_type
        key.set_contents_from_string(thumb['data'], policy='public-read')

    image = Image(
        key=image_key,
        extension=extension,
        hash=sha1(image_data).hexdigest(),
        description=description,
        album=album,
        photographer=photographer,
        credits=credits,
        licence=licence,
        exif=exif_json,
        uploader=uploader,
        width=pil_image.size[0],
        height=pil_image.size[1])
    image.save()

    for tag in [tag.lower() for tag in image_file_tags + tags]:
        obj, created = Tag.objects.get_or_create(name=tag)
        image.tags.add(obj)

    return image

def full_archive_search(query):
    images = Image.objects.all()
    for word in query.split():
        images = images.filter(
            Q(description__icontains=word) |
            Q(album__name__icontains=word) |
            Q(photographer__icontains=word) |
            Q(credits__icontains=word) |
            Q(licence__icontains=word) |
            Q(tags__name__icontains=word))
    images = images.distinct()

    albums = Album.objects.all()
    for word in query.split():
        albums = albums.filter(name__icontains=word)
    albums = albums.distinct()

    return albums, images

# Lol, I bet there's a much easier way to do this, but whatever, this works for now.
def divide_for_three_columns(albums):
    bulk = len(albums) / 3
    rest = len(albums) % 3

    if rest > 0:
        first = bulk + 1
        rest -= 1
    else:
        first = bulk

    if rest > 0:
        second = first + bulk + 1
    else:
        second = first + bulk

    return [albums[:first], albums[first:second], albums[second:]]

def parse_objects(parents, albums, images):
    objects = {'parents': [], 'albums': [], 'images': []}
    for parent in parents:
        objects['parents'].append({'id': parent.id, 'name': parent.name})
    for album in albums:
        objects['albums'].append({'id': album.id, 'name': album.name})
    for image in images:
        objects['images'].append({'key': image.key, 'extension': image.extension,
            'width': image.width, 'height': image.height,
            'photographer': image.photographer, 'description': image.description})
    return objects


def list_parents(album):
    parents = []
    parents.append(album)
    while(album.parent is not None):
        album = Album.objects.get(id=album.parent.id)
        parents.insert(0, album)
    return parents

def list_parents_values(album):
    parents = []
    parents.append({'id': album.id, 'name': album.name})
    while(album.parent is not None):
        album = Album.objects.get(id=album.parent.id)
        parents.insert(0, {'id': album.id, 'name': album.name})
    return parents

def get_exif_tags(pil_image):
    try:
        exif = {}
        if hasattr(pil_image, '_getexif') and pil_image._getexif() is not None:
            for tag, value in pil_image._getexif().items():
                if tag == 37500:
                    # MakerNote data, see: https://en.wikipedia.org/wiki/Exchangeable_image_file_format#MakerNote_data
                    continue
                try:
                    # No more known binary tags. Attempt to recursively encode the data:
                    json.dumps(value)
                except UnicodeDecodeError:
                    # Skip this tag, it's not a text string
                    # TODO: Should log a warning with the tag string here.
                    continue
                exif[PIL.ExifTags.TAGS.get(tag, tag)] = value
    except IOError:
        # Calling _getexif() on some select images raises IOError("not enough data").
        # Not sure what that means but we'll ignore exif data on those images for now.
        return {}
    except IndexError:
        # Invalid exif data; ignore. See:
        # - https://sentry.turistforeningen.no/turistforeningen/sherpa/group/33881/events/1272445/
        # - https://github.com/python-pillow/Pillow/issues/518
        return {}

def create_thumb(pil_image, extension, size):
    fp = StringIO()
    img_copy = pil_image.copy()
    img_copy.thumbnail([size, size], PIL.Image.ANTIALIAS)
    img_copy.save(fp, standardize_extension(extension))
    return fp.getvalue()

def standardize_extension(extension):
    # Force lowercase
    extension = extension.lower()

    # Some image types have common extensions (like .jpg) which are not recognized by PIL
    if extension == 'jpg':
        return 'jpeg'
    elif extension == 'tif':
        return 'tiff'
    else:
        return extension

def download_images(request, images, image_set_name):
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(s3_bucket())

    def set_exif_tag(metadata, key, value):
        if key in metadata:
            metadata[key].value = value
        else:
            metadata[key] = pyexiv2.ExifTag(key, value)

    def download_image_with_retry(image, bucket, tmp_file, tmp_file_index, zip_archive, file_count, tries=5):
        """
        Tries to download an image from S3, and if an SSLError occurs, resets the boto connection and retries the
        download. This was implemented because we experienced this error occasionally for large album downloads.
        The idea was originally to use funcy[1] with the @retry decorator, but we discovered that we need to change
        state on error (i.e. reset the boto connection), which AFAIK couldn't be done with funcy; hence this custom
        implementation.
        [1] See https://github.com/Suor/funcy and
            http://hackflow.com/blog/2014/06/22/why-every-language-needs-its-underscore/
        """
        try:
            image_key = bucket.get_key("%s%s.%s" % (settings.AWS_IMAGEGALLERY_PREFIX, image.key, image.extension))
            image_data = image_key.get_contents_as_string()

            # Write relevant exif data
            metadata = pyexiv2.ImageMetadata.from_buffer(image_data)
            metadata.read()
            set_exif_tag(metadata, 'Exif.Image.ImageDescription', image.description)
            set_exif_tag(metadata, 'Exif.Image.Artist', image.photographer)
            set_exif_tag(metadata, 'Exif.Image.Copyright', image.licence)
            metadata.write()

            # And add the modified image to the zip archive
            if image.photographer == '':
                image_filename = '%s-%s.%s' % (image_set_name, file_count, image.extension)
            else:
                image_filename = '%s-%s-%s.%s' % (image_set_name, file_count, image.photographer, image.extension)
            zip_archive.writestr(image_filename.encode('ascii', 'ignore'), metadata.buffer)

            # Rewind the memory file back, read the written data, and yield it to our response,
            # while we'll go fetch the next file from S3
            next_index = tmp_file.tell()
            tmp_file.seek(tmp_file_index)
            return next_index, tmp_file.read()
        except Exception:
            logger.warning(u"Feil ved albumnedlasting (prøver igjen automatisk)",
                exc_info=sys.exc_info(),
                extra={'request': request}
            )

            if tries <= 0:
                raise

            # Reset the conncetion and try again
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(s3_bucket())
            return download_image_with_retry(image, bucket, tmp_file, tmp_file_index, zip_archive, file_count, tries=tries-1)

    def build_zipfile():
        with tempfile.TemporaryFile() as tmp_file:
            zip_archive = zipfile.ZipFile(tmp_file, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
            tmp_file_index = 0 # Used to keep track of the amount of written data each iteration

            for file_count, image in enumerate(images, start=1):
                tmp_file_index, data = download_image_with_retry(image, bucket, tmp_file, tmp_file_index, zip_archive, file_count)
                yield data

            # Now close the archive and yield the final piece of data written
            zip_archive.close()
            tmp_file.seek(tmp_file_index)
            yield tmp_file.read()

    response = HttpResponse(build_zipfile(), content_type='application/x-zip-compressed')
    response['Content-Disposition'] = 'attachment; filename="%s.zip"' % image_set_name.encode('utf-8')
    return response
