from django.core.urlresolvers import reverse

from core.models import Zipcode, FocusCountry
from focus.models import Actor
from enrollment.util import invalid_location, invalid_existing, AGE_YOUTH

from datetime import datetime

def validate(enrollment, require_location, require_existing):
    if enrollment.users.count() == 0:
        return {
            'valid': False,
            'redirect': ["enrollment.views.registration"]
        }
    # Verify that at least one member has valid contact information
    if not any([u.is_valid(require_contact_info=True) for u in enrollment.users.all()]):
        return {
            'valid': False,
            'message': 'contact_missing',
            'redirect': ["enrollment.views.registration"]
        }
    # Verify that all members are otherwise valid (without contact information required)
    for u in enrollment.users.all():
        if not u.is_valid():
            # Redirect back to edit this first invalid user. If others are also invalid, let them
            # figure that out on the next attempt to validate.
            return {
                'valid': False,
                'message': 'user_invalid',
                'redirect': ["enrollment.views.registration", u.id]
            }
    if require_location:
        if not validate_location(enrollment):
            return {
                'valid': False,
                'redirect': ["%s?%s" % (reverse("enrollment.views.household"), invalid_location)]
            }
    if require_existing:
        if enrollment.existing_memberid != '' and not validate_existing(enrollment):
            return {
                'valid': False,
                'redirect': ["%s?%s" % (reverse("enrollment.views.household"), invalid_existing)]
            }

    return {
        'valid': True
    }

def validate_location(enrollment):
    # Country does not exist
    if not FocusCountry.objects.filter(code=enrollment.country).exists():
        return False

    # No address provided for other countries than Norway
    # (Some Norwegians actually don't have a street address)
    if enrollment.country != 'NO':
        if enrollment.address1.strip() == '':
            return False

    # Require zipcode for all scandinavian countries
    if enrollment.country == 'NO' or enrollment.country == 'SE' or enrollment.country == 'DK':
        if enrollment.zipcode.strip() == '':
            return False

    if enrollment.country == 'SE' or enrollment.country == 'DK':
        # No area provided
        if enrollment.area.strip() == '':
            return False

    if enrollment.country == 'NO':
        # Zipcode does not exist
        if not Zipcode.objects.filter(zipcode=enrollment.zipcode).exists():
            return False

    # All tests passed!
    return True

def validate_existing(enrollment):
    try:
        actor = Actor.objects.get(memberid=enrollment.existing_memberid)
    except (Actor.DoesNotExist, ValueError):
        return False

    if datetime.now().year - actor.birth_date.year < AGE_YOUTH:
        return False

    if actor.is_household_member():
        return False

    if actor.get_clean_address().country.code != enrollment.country:
        return False

    if enrollment.country == 'NO' and actor.get_clean_address().zipcode.zipcode != enrollment.zipcode:
        return False

    return True
