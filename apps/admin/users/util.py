# encoding: utf-8
from smtplib import SMTPException
from ssl import SSLError

from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

def send_access_granted_email(user, forening, user_providing_access):
    try:
        subject = "Du har fått tilgang til nye Sherpa"
        context = Context({
            'user': user,
            'forening': forening,
            'user_providing_access': user_providing_access,
        })
        message = render_to_string('common/admin/users/email_access_granted.txt', context)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.get_email()])
        return True
    except (SMTPException, SSLError):
        return False
