from django import template

from user.models import AssociationRole

register = template.Library()

@register.filter
def role(association, profile):
    return AssociationRole.objects.get(association=association, profile=profile).role
