from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

from core import validator
from core.models import Zipcode, FocusCountry
from focus.models import Actor
from enrollment.util import invalid_location, invalid_existing, AGE_YOUTH

from datetime import datetime

def validate(request, require_location, require_existing):
    if not 'enrollment' in request.session:
        return redirect("enrollment.views.registration")
    if len(request.session['enrollment']['users']) == 0:
        return redirect("enrollment.views.registration")
    if not validate_youth_count(request.session['enrollment']['users']):
        messages.error(request, 'too_many_underage')
        return redirect("enrollment.views.registration")
    if not validate_user_contact(request.session['enrollment']['users']):
        messages.error(request, 'contact_missing')
        return redirect("enrollment.views.registration")
    if require_location:
        if not 'location' in request.session['enrollment'] or not validate_location(request.session['enrollment']['location']):
            return redirect("%s?%s" % (reverse("enrollment.views.household"), invalid_location))
    if require_existing:
        if request.session['enrollment']['existing'] != '' and not validate_existing(request.session['enrollment']['existing'], request.session['enrollment']['location']['zipcode'], request.session['enrollment']['location']['country']):
            return redirect("%s?%s" % (reverse("enrollment.views.household"), invalid_existing))

def validate_user(user):
    # Name or address is empty
    if not validator.name(user['name']):
        return False

    # Gender is not set
    if user.get('gender', '') != 'm' and user.get('gender', '') != 'f':
        return False

    # Check phone number only if supplied
    if not validator.phone(user['phone'], req=False):
        return False

    # Email is non-empty (empty is allowed) and doesn't match an email
    if not validator.email(user['email'], req=False):
        return False

    # Date of birth is not valid format (%d.%m.%Y)
    # Will be unicode when posted, but datetime when saved
    if isinstance(user['dob'], unicode):
        try:
            datetime.strptime(user['dob'], "%d.%m.%Y")
        except ValueError:
            return False
    elif not isinstance(user['dob'], datetime):
        return False

    # Birthyear is below 1900 (MSSQLs datetime datatype will barf)
    # Same as above, will be unicode when posted, but datetime when saved
    if isinstance(user['dob'], unicode):
        date_to_test = datetime.strptime(user['dob'], "%d.%m.%Y")
    else:
        date_to_test = user['dob']
    if date_to_test.year < 1900:
        return False

    # All tests passed!
    return True

def validate_location(location):
    # Country does not exist
    if not FocusCountry.objects.filter(code=location['country']).exists():
        return False

    # No address provided for other countries than Norway
    # (Some Norwegians actually don't have a street address)
    if location['country'] != 'NO':
        if location['address1'].strip() == '':
            return False

    # Require zipcode for all scandinavian countries
    if location['country'] == 'NO' or location['country'] == 'SE' or location['country'] == 'DK':
        if location['zipcode'].strip() == '':
            return False

    if location['country'] == 'SE' or location['country'] == 'DK':
        # No area provided
        if location['area'].strip() == '':
            return False

    if location['country'] == 'NO':
        # Zipcode does not exist
        if not Zipcode.objects.filter(zipcode=location['zipcode']).exists():
            return False

    # All tests passed!
    return True

# Check that at least one member has valid phone and email
def validate_user_contact(users):
    for user in users:
        if validator.phone(user['phone']) and validator.email(user['email']):
            return True
    return False

def validate_existing(id, zipcode, country):
    try:
        actor = Actor.objects.get(memberid=id)
    except (Actor.DoesNotExist, ValueError):
        return False

    if datetime.now().year - actor.birth_date.year < AGE_YOUTH:
        return False

    if actor.is_household_member():
        return False

    if actor.get_clean_address().country.code != country:
        return False

    if country == 'NO' and actor.get_clean_address().zipcode.zipcode != zipcode:
        return False

    return True

def validate_youth_count(users):
    # Based on order number length, which is 32.
    # MemberID is 7 chars, order number format is I[_<memberid>]+ so 4 users = 33 chars.
    if len(users) <= 3:
        return True
    at_least_one_main_member = False
    for user in users:
        if user['age'] >= AGE_YOUTH:
            at_least_one_main_member = True
            break
    return at_least_one_main_member
