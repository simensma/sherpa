from hashlib import sha1
import json

from django.conf import settings
from django.http import HttpResponse

import boto

from core.util import s3_bucket

def handle_upload(request, site):
    file = request.FILES['files[]'] # Default jquery-file-upload name. Should always be a single file

    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(s3_bucket())

    # We'll have to read the entire file instead of streaming chunks because we need all its data to calculate the
    # sha1 name
    data = file.read()
    sha1_hash = sha1(data).hexdigest()
    extension = file.name.split(".")[-1].lower()

    key = bucket.new_key("%s/%s.%s" % (settings.AWS_FILEUPLOAD_PREFIX, sha1_hash, extension))
    key.content_type = file.content_type
    key.set_contents_from_string(data, policy='public-read')

    return HttpResponse(json.dumps({
        'files': [{
            'name': file.name,
            'size': file.size,
            'url': 'https://%s/%s/%s.%s' % (
                s3_bucket(ssl=True),
                settings.AWS_FILEUPLOAD_PREFIX,
                sha1_hash,
                extension,
            ),
        }],
    }))
