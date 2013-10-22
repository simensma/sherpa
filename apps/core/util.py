# Core utility methods that aren't views

from django.conf import settings

from user.models import AssociationRole

from datetime import date
import re

def use_image_thumb(url, preferred_size):
    if url.find("%s/%s" % (settings.AWS_BUCKET, settings.AWS_IMAGEGALLERY_PREFIX)) == -1:
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

def association_user_role(association, user):
    try:
        return AssociationRole.objects.get(association=association, user=user).role
    except AssociationRole.DoesNotExist:
        # This might be a related association where we're admin beacuse we're admin for a parent. Check it
        role = AssociationRole.objects.filter(association=association, user=user)
        while not role.exists() or role[0].role != 'admin':
            association = association.parent
            if association is None:
                raise NoRoleRelationException
            role = AssociationRole.objects.filter(association=association, user=user)
        return role[0].role

class NoRoleRelationException(Exception):
    """Raised when the Association does not have a related role"""

def current_membership_year_start():
    """
    Returns the date object for the current membership year start.
    Usually some date near October/November.
    """
    today = date.today()
    for year in settings.MEMBERSHIP_YEAR_START:
        if year.year == today.year:
            return year
    # The current year isn't specified - create a new date with the month of the latest specified year
    month = max(settings.MEMBERSHIP_YEAR_START).month
    return date(year=today.year, month=month, day=1)

def previous_membership_year_start():
    """
    Returns the date object for the previous' membership year start, for those
    rare cases where that's interesting.
    """
    today = date.today()
    for year in settings.MEMBERSHIP_YEAR_START:
        if year.year == today.year - 1:
            return year
    # The exact year isn't defined - find the newest one before last year
    candidates = [y for y in settings.MEMBERSHIP_YEAR_START if y.year < today.year - 1]
    # Note that we'll intentionally let max() raise ValueError if candidates is empty
    month = max(candidates).month
    return date(year=(today.year - 1), month=month, day=1)
