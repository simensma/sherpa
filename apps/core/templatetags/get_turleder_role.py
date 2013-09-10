# encoding: utf-8
from django import template

register = template.Library()

@register.filter
def get_turleder_role(user, role):
    roles = [t for t in user.turledere.all() if t.role == role]
    if len(roles) == 0:
        return None
    elif len(roles) > 1:
        raise Exception("Turleder har registrert >1 sertifikat for én turlederrolle.")
    else:
        return roles[0]
