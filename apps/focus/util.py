# encoding: utf-8

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

def get_membership_type_by_code(code):
    return [t for t in MEMBERSHIP_TYPES if t['code'] == code][0]

def get_membership_type_by_codename(codename):
    return [t for t in MEMBERSHIP_TYPES if t['codename'] == codename][0]
