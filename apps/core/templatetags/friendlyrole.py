from django import template

from user.models import AssociationRole

register = template.Library()

@register.filter
def friendlyrole(role):
    return AssociationRole.friendly_role(role)
