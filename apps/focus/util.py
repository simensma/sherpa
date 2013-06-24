# encoding: utf-8

# A few defined service codes, consult Focus for more
FJELLOGVIDDE_SERVICE_CODE = 151
YEARBOOK_SERVICE_CODES = [152, 153, 154]
FOREIGN_POSTAGE_SERVICE_CODE = 155

# Actor endcodes (reasons for terminating membership).
# These aren't really properly documented yet, to resolve codes/reasons consult Focus.
ACTOR_ENDCODE_DUBLETT = 21

MEMBERSHIP_TYPES = [
    {'code': 101, 'codename': u'main', 'name': u'Hovedmedlem'},
    {'code': 102, 'codename': u'youth', 'name': u'Ungdomsmedlem'},
    {'code': 103, 'codename': u'senior', 'name': u'Honnørmedlem'},
    {'code': 104, 'codename': u'lifelong', 'name': u'Livsvarig medlem'},
    {'code': 105, 'codename': u'child', 'name': u'Barnemedlem'},
    {'code': 106, 'codename': u'school', 'name': u'Skoleungdomsmedlem'},
    {'code': 107, 'codename': u'household', 'name': u'Husstandsmedlem'},
    # Note: type 108 is deprecated
    {'code': 108, 'codename': u'household_without_main', 'name': u'Husstandsmedlem uten hovedmedlem'},
    {'code': 109, 'codename': u'lifelong_household', 'name': u'Livsvarig husstandsmedlem'}
]

# We don't usually specify max_length on Focus models. The address model contains a field
# length of 40 chars which is very short, so we'll specify that here and use it for validation.
ADDRESS_FIELD_MAX_LENGTH = 40

def get_membership_type_by_code(code):
    return [t for t in MEMBERSHIP_TYPES if t['code'] == code][0]

def get_membership_type_by_codename(codename):
    return [t for t in MEMBERSHIP_TYPES if t['codename'] == codename][0]
