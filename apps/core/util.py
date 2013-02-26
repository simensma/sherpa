# Core utility methods that aren't views

from django.conf import settings

import re

def use_image_thumb(url, preferred_size):
    if url.find("%s/%s" % (settings.AWS_BUCKET, settings.AWS_IMAGEGALLERY_PREFIX)) != -1:
        pre, post = url.rsplit('.', 1)

        # If it's already a thumb, use the original
        for thumb in settings.THUMB_SIZES:
            if pre.endswith('-%s' % thumb):
                pre = re.sub('-%s' % thumb, '', pre)

        larger_than_preferred = [t for t in settings.THUMB_SIZES if t >= preferred_size]
        if len(larger_than_preferred) == 0:
            # No thumbs are larger than the requested size, just use the original image
            return "%s.%s" % (pre, post)
        else:
            appropriate_size = min(larger_than_preferred)
        return "%s-%s.%s" % (pre, appropriate_size, post)
    return url
