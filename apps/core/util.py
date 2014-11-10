# Core utility methods that aren't views

from datetime import date
import re

from django.conf import settings

def use_image_thumb(url, preferred_size):
    if url.find("%s/%s" % (s3_bucket(), settings.AWS_IMAGEGALLERY_PREFIX)) == -1:
        # Not a file from our image archive, don't modify it
        return url

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

def membership_year_start(year=None):
    """
    Returns the date set for the membership year start, see settings.MEMBERSHIP_YEAR_START.
    """
    if year is None:
        year = date.today().year

    for dates in settings.MEMBERSHIP_YEAR_START:
        if dates['public_date'].year == year:
            return dates

    # At this point, there's no entry for the current year. Use the dates from the latest defined year.
    candidates = [d for d in settings.MEMBERSHIP_YEAR_START if d['public_date'].year <= year]
    dates = max(candidates, key=lambda d: d['public_date'])

    # Return a fake date set based on the values we got
    return {
        'initiation_date': date(year=year, month=dates['initiation_date'].month, day=dates['initiation_date'].day),
        'actual_date': date(year=year, month=dates['actual_date'].month, day=dates['actual_date'].day),
        'public_date': date(year=year, month=dates['public_date'].month, day=dates['public_date'].day),
    }

def s3_bucket(ssl=False):
    if not ssl:
        if not settings.DEBUG:
            return settings.AWS_BUCKET
        else:
            return settings.AWS_BUCKET_DEV
    else:
        if not settings.DEBUG:
            return settings.AWS_BUCKET_SSL
        else:
            return settings.AWS_BUCKET_SSL_DEV

# Multi-dimensional Form Array Parser by Herman Schaaf (@ironzeb)
# http://www.ironzebra.com/code/23
def parse_html_array(post, name):
    dictionary = {}

    for key in post.keys():
        if key.startswith(name):
            rest = key[len(name):]

            # Split the string into different components
            parts = [p[:-1] for p in rest.split('[')][1:]

            # Prevent parsing non integer array keys (such as tmp)
            try:
                id = int(parts[0])
            except ValueError:
                continue

            # Add a new dictionary if it doesn't exist yet
            if id not in dictionary:
                dictionary[id] = {}

            # Add the information to the dictionary
            dictionary[id][parts[1]] = post.get(key)

    return dictionary
