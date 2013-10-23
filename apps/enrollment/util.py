# encoding: utf-8
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string
from django.db import transaction, connections

from focus.models import Enrollment
from focus.util import PAYMENT_METHOD_CODES, get_membership_type_by_codename

from datetime import datetime, timedelta
import sys
import logging
from smtplib import SMTPException


# Number of days the temporary membership proof is valid
TEMPORARY_PROOF_VALIDITY = 14

KEY_PRICE = 100
FOREIGN_SHIPMENT_PRICE = 100

# GET parameters used for error handling (still a few remaining)
invalid_location = 'ugyldig-adresse'
invalid_existing = 'ugyldig-eksiserende-hovedmedlem'

EMAIL_FROM = "Den Norske Turistforening <medlem@turistforeningen.no>"
EMAIL_SUBJECT_SINGLE = "Velkommen som medlem!"
EMAIL_SUBJECT_MULTIPLE = "Velkommen som medlemmer!"

# Hardcoded ages
AGE_SENIOR = 67
AGE_MAIN = 27
AGE_YOUTH = 19
AGE_SCHOOL = 13

logger = logging.getLogger('sherpa')

def current_template_layout(request):
    """
    Currently, enrollment could be initiated from:
    - The regular websites (uses main layout)
    - DNT Connect (should differentiate between clients, but for now uses DNT Oslos template)
    """
    if 'dntconnect' in request.session:
        return {'current_layout': 'main/connect/layouts/columbus.html'}
    else:
        return {'current_layout': 'main/layout.html'}

def prepare_and_send_email(request, users, association, location, payment_method, price_sum):
    if len(users) == 1:
        subject = EMAIL_SUBJECT_SINGLE
        template = '%s-single' % payment_method
    else:
        subject = EMAIL_SUBJECT_MULTIPLE
        template = '%s-multiple' % payment_method
    # proof_validity_end is not needed for the 'card' payment_method, but ignore that
    proof_validity_end = datetime.now() + timedelta(days=TEMPORARY_PROOF_VALIDITY)
    for user in users:
        try:
            if user['email'] == '':
                continue

            context = Context({
                'user': user,
                'users': users,
                'association': association,
                'location': location,
                'proof_validity_end': proof_validity_end,
                'price_sum': price_sum
            })
            message = render_to_string('main/enrollment/result/emails/%s.txt' % template, context)
            send_mail(subject, message, EMAIL_FROM, [user['email']])
        except SMTPException:
            # Silently log and ignore this error. The user will have to do without email receipt.
            logger.warning(u"Klarte ikke å sende innmeldingskvitteringepost",
                exc_info=sys.exc_info(),
                extra={'request': request}
            )

def updateIndices(session):
    i = 0
    for user in session['enrollment']['users']:
        user['index'] = i
        i += 1

def price_of(age, household, price):
    if household:
        return min(price_of_age(age, price), price.household)
    else:
        return price_of_age(age, price)

def price_of_age(age, price):
    if age >= AGE_SENIOR:    return price.senior
    elif age >= AGE_MAIN:    return price.main
    elif age >= AGE_YOUTH:   return price.youth
    elif age >= AGE_SCHOOL:  return price.school
    else:                    return price.child

def type_of(age, household):
    if household and age >= AGE_YOUTH:
        return get_membership_type_by_codename('household')['name']
    elif age >= AGE_SENIOR:
        return get_membership_type_by_codename('senior')['name']
    elif age >= AGE_MAIN:
        return get_membership_type_by_codename('main')['name']
    elif age >= AGE_YOUTH:
        return get_membership_type_by_codename('youth')['name']
    elif age >= AGE_SCHOOL:
        return get_membership_type_by_codename('school')['name']
    else:
        return get_membership_type_by_codename('child')['name']

def polite_title(str):
    # If the string is all lowercase or uppercase, apply titling for it
    # Else, assume that the specified case is intentional
    if str.islower() or str.isupper():
        return str.title()
    else:
        return str

def add_focus_user(name, dob, age, gender, location, phone, email, can_have_yearbook, wants_yearbook, linked_to, payment_method, price):
    first_name, last_name = name.rsplit(' ', 1)
    gender = 'M' if gender == 'm' else 'K'
    language = 'nb_no'
    type = focus_type_of(age, linked_to is not None)
    payment_method = PAYMENT_METHOD_CODES[payment_method]
    price = price_of(age, linked_to is not None, price)
    linked_to = '' if linked_to is None else str(linked_to)
    if location['country'] == 'NO':
        # Override yearbook value for norwegians based on age and household status
        yearbook = focus_receive_yearbook(age, linked_to)
    else:
        # Foreigners need to pay shipment price for the yearbook, so if they match the
        # criteria to receive it, let them choose whether or not to get it
        yearbook = can_have_yearbook and wants_yearbook
        if yearbook:
            price += FOREIGN_SHIPMENT_PRICE
    if yearbook:
        yearbook_type = 152
    else:
        yearbook_type = ''

    adr1 = location['address1']
    if location['country'] == 'NO':
        adr2 = ''
        adr3 = ''
        zipcode = location['zipcode']
        area = location['area']
    elif location['country'] == 'DK' or location['country'] == 'SE':
        adr2 = ''
        adr3 = "%s-%s %s" % (location['country'], location['zipcode'], location['area'])
        zipcode = '0000'
        area = ''
    else:
        adr2 = location['address2']
        adr3 = location['address3']
        zipcode = '0000'
        area = ''

    # Fetch and increment memberid with stored procedure
    with transaction.commit_manually():
        cursor = connections['focus'].cursor()
        cursor.execute("exec sp_custTurist_updateMemberId")
        memberid = cursor.fetchone()[0]
        connections['focus'].commit_unless_managed()

    user = Enrollment(
        memberid=memberid,
        last_name=last_name,
        first_name=first_name,
        birth_date=dob,
        gender=gender,
        linked_to=linked_to,
        adr1=adr1,
        adr2=adr2,
        adr3=adr3,
        country_code=location['country'],
        phone_home='',
        email=email,
        receive_yearbook=yearbook,
        type=type,
        yearbook=yearbook_type,
        payment_method=payment_method,
        phone_mobile=phone,
        zipcode=zipcode,
        area=area,
        language=language,
        totalprice=price
    )
    user.save()
    return memberid

def focus_type_of(age, household):
    if household and age >= AGE_YOUTH:
        return get_membership_type_by_codename('household')['code']
    elif age >= AGE_SENIOR:
        return get_membership_type_by_codename('senior')['code']
    elif age >= AGE_MAIN:
        return get_membership_type_by_codename('main')['code']
    elif age >= AGE_YOUTH:
        return get_membership_type_by_codename('youth')['code']
    elif age >= AGE_SCHOOL:
        return get_membership_type_by_codename('school')['code']
    else:
        return get_membership_type_by_codename('child')['code']

def focus_receive_yearbook(age, linked_to):
    if linked_to != '':
        return False
    elif age >= AGE_YOUTH:
        return True
    else:
        return False
