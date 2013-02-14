# encoding: utf-8
from django.core.cache import cache
from django.conf import settings

import md5
import hashlib

from sherpa25.models import Member

# This returns a username value based on the email address.
# Define it as the first 30 hex-characters of the MD5 hash of the stripped, lowercase email.
# This is because the username field has a 30 character max length, which makes it unsuitable for
# actual e-mail addresses. This gives a 16^30 collision chance which is acceptable.
def username(email):
    return md5.new(email.strip().lower()).hexdigest()[:30]

# Checks whether the given IP address has performed more than the allowed amount of lookups
# on memberid + zipcode. This is because since there are a relatively low amount of total zipcodes
# (< 10000), this can easily be bruteforced, given the memberid.
# Notes:
# 1. The odds for someone wanting to do this are extremely low, but since the security hole does exist
#    we should account for it, however simply.
# 2. This "authentication method" (memberid + zipcode) is not very secure anyway, since it's easy
#    to get that information from someone.
def memberid_lookups_exceeded(ip_address):
    lookups = cache.get('memberid_zipcode_lookups.%s' % ip_address)
    if lookups is None:
        cache.set('memberid_zipcode_lookups.%s' % ip_address, 1, settings.MEMBERID_LOOKUPS_BAN)
    else:
        if lookups < settings.MEMBERID_LOOKUPS_LIMIT:
            cache.set('memberid_zipcode_lookups.%s' % ip_address, lookups + 1, settings.MEMBERID_LOOKUPS_BAN)
        else:
            return True
    return False

def authenticate_sherpa2_user(email, password):
    sha1 = hashlib.sha1()
    sha1.update(password)
    hashed_password = sha1.hexdigest()
    try:
        return Member.objects.get(email=email, password=hashed_password)
    except Member.DoesNotExist:
        return None
