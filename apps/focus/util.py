# encoding: utf-8

# A few defined service codes, consult Focus for more
FJELLOGVIDDE_SERVICE_CODE = 151
YEARBOOK_SERVICE_CODES = [152, 153, 154]
FOREIGN_POSTAGE_SERVICE_CODES = [155, 156, 157]

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

# Payment method codes for the field in focus.models.Enrollment.payment_method
PAYMENT_METHOD_CODES = {
    'card': 4,
    'invoice': 1
}

def get_membership_type_by_code(code):
    return [t for t in MEMBERSHIP_TYPES if t['code'] == code][0]

def get_membership_type_by_codename(codename):
    return [t for t in MEMBERSHIP_TYPES if t['codename'] == codename][0]

def get_enrollment_email_matches(email):
    """
    Soo, it seems the focus.models.Enrollment.email field is of the 'ntext' type, which is completely wrong.
    We can't perform lookups on it without casting it to nvarchar, so we'll have to do this with a raw query.
    Yes, this is truly truly horrible. However, at least Django still takes care of SQL injection, so as long
    as the query is correct, this *should* be all right. The current query would look like this with ORM:
    Enrollment.get_active().filter(email=email)
    """
    from focus.models import Enrollment
    query = 'select * from %s where (("Paymethod" = %s or "Paymethod" = %s ) and "SubmittedDt" is null and Cast(Email as nvarchar(max)) = %s )' % (Enrollment._meta.db_table, '%s', '%s', '%s')
    params = [PAYMENT_METHOD_CODES['card'], PAYMENT_METHOD_CODES['invoice'], email]
    return Enrollment.objects.raw(query, params)
