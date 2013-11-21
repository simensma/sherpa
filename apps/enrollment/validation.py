from django.core.urlresolvers import reverse

from core.models import Zipcode, FocusCountry
from focus.models import Actor
from enrollment.util import invalid_location, invalid_existing, AGE_YOUTH

from datetime import datetime

def validate(enrollment, require_location, require_existing):
    if enrollment.users.count() == 0:
        return {
            'valid': False,
            'redirect': "enrollment.views.registration"
        }
    if not validate_youth_count(enrollment):
        return {
            'valid': False,
            'message': 'too_many_underage',
            'redirect': "enrollment.views.registration"
        }
    if not any([u.is_valid(require_contact_info=True) for u in enrollment.users.all()]):
        return {
            'valid': False,
            'message': 'contact_missing',
            'redirect': "enrollment.views.registration"
        }
    if require_location:
        if not validate_location(enrollment):
            return {
                'valid': False,
                'redirect': "%s?%s" % (reverse("enrollment.views.household"), invalid_location)
            }
    if require_existing:
        if enrollment.existing_memberid != '' and not validate_existing(enrollment):
            return {
                'valid': False,
                'redirect': "%s?%s" % (reverse("enrollment.views.household"), invalid_existing)
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

def validate_youth_count(enrollment):
    # Based on order number length, which is 32.
    # MemberID is 7 chars, order number format is I[_<memberid>]+ so 4 users = 33 chars.
    if enrollment.users.count() <= 3:
        return True
    at_least_one_main_member = False
    for user in enrollment.users.all():
        if user.get_age() >= AGE_YOUTH:
            at_least_one_main_member = True
            break
    return at_least_one_main_member
