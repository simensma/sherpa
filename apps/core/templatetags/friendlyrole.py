from django import template

from user.models import ForeningRole

register = template.Library()

@register.filter
def friendlyrole(role):
    return ForeningRole.friendly_role(role)
