from core.util import s3_bucket
from django.template import Library
from django.conf import settings

register = Library()

@register.filter
def image_size(source, size):
    """
    Return URL with specified width appended if it is local and matches a size in settings.THUMB_SIZES
    """

    # Only local images is applicable for this filter
    local_image_path = '%s/%s' % (s3_bucket(), settings.AWS_IMAGEGALLERY_PREFIX)
    local_image_path_ssl = '%s/%s' % (s3_bucket(ssl=True), settings.AWS_IMAGEGALLERY_PREFIX)

    if not local_image_path in source and not local_image_path_ssl in source:
        # Not an image from the image gallery; don't touch it
        return source

    # Proceed only if passed width exists
    if size not in settings.THUMB_SIZES:
        return source

    name, extension = source.rsplit('.', 1)
    return '%s-%s.%s' % (name, size, extension)
