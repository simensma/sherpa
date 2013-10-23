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

def membership_year_start(year=date.today().year):
    """
    Returns the date set for the membership year start, see settings.MEMBERSHIP_YEAR_START.
    """
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
