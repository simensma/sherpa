from django import template

register = template.Library()

@register.filter
def has_membership_type(user, codename):
    return user.has_membership_type(codename)
