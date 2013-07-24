from django import template

from core.util import association_user_role, NoRoleRelationException

register = template.Library()

# Finds the role for an association-user relation,
# Note, this is not currently in use (and neither is the util method it calls)
# It might be useful later though, so it'll stay for now.
@register.filter
def role_for(association, user):
    try:
        return association_user_role(association, user)
    except NoRoleRelationException:
        return ''
