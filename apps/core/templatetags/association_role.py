from django import template

from core.util import association_profile_role, NoRoleRelationException

register = template.Library()

# Finds the role for an association-profile relation,
# Note, this is not currently in use (and neither is the util method it calls)
# It might be useful later though, so it'll stay for now.
@register.filter
def role_for(association, profile):
    try:
        return association_profile_role(association, profile)
    except NoRoleRelationException:
        return ''
