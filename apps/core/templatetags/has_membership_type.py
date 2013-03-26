from django import template

register = template.Library()

@register.filter
def has_membership_type(actor, codename):
    return actor.has_membership_type(codename)
