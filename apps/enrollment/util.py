# encoding: utf-8
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string

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

def get_or_create_enrollment(request):
    from enrollment.models import Enrollment
    def create_enrollment(request):
        enrollment = Enrollment(
            state='registration',
            accepts_conditions=False,
        )
        enrollment.save()
        request.session['enrollment'] = enrollment.pk
        return enrollment

    if not 'enrollment' in request.session:
        enrollment = create_enrollment(request)
    else:
        # Temporary check for the old session structure, shouldn't be needed longer than
        # the session expiry date (2 weeks from this commit) I think?
        if type(request.session['enrollment']) == dict:
            # Note that we could send the user a message here, but don't bother. We'll deploy this
            # when very few are online, and there will be many more false positives than true positives,
            # so we prefer not to confuse those and rather confuse the true positives just a little bit
            # (they'll just have to fill the form out an extra time).
            logger.warning(u"Bruker med gammel enrollment-struktur må starte innmelding på nytt",
                extra={
                    'request': request,
                    'old_enrollment': request.session['enrollment'],
                }
            )
            del request.session['enrollment']
            enrollment = create_enrollment(request)

        try:
            enrollment = Enrollment.objects.get(id=request.session['enrollment'])
        except Enrollment.DoesNotExist:
            enrollment = create_enrollment(request)
    return enrollment

def prepare_and_send_email(request, enrollment):
    if enrollment.users.count() == 1:
        subject = EMAIL_SUBJECT_SINGLE
        template = '%s-single' % enrollment.payment_method
    else:
        subject = EMAIL_SUBJECT_MULTIPLE
        template = '%s-multiple' % enrollment.payment_method
    # proof_validity_end is not needed for the 'card' payment_method, but ignore that
    proof_validity_end = datetime.now() + timedelta(days=TEMPORARY_PROOF_VALIDITY)
    for user in enrollment.users.all():
        try:
            if user.email == '':
                continue

            context = Context({
                'user': user,
                'users': enrollment.users.all(),
                'proof_validity_end': proof_validity_end,
            })
            message = render_to_string('main/enrollment/result/emails/%s.txt' % template, context)
            send_mail(subject, message, EMAIL_FROM, [user.email])
        except SMTPException:
            # Silently log and ignore this error. The user will have to do without email receipt.
            logger.warning(u"Klarte ikke å sende innmeldingskvitteringepost",
                exc_info=sys.exc_info(),
                extra={'request': request}
            )

def polite_title(str):
    # If the string is all lowercase or uppercase, apply titling for it
    # Else, assume that the specified case is intentional
    if str.islower() or str.isupper():
        return str.title()
    else:
        return str
