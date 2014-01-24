from django import template

from core.util import forening_user_role, NoRoleRelationException

register = template.Library()

# Finds the role for an forening-user relation,
# Note, this is not currently in use (and neither is the util method it calls)
# It might be useful later though, so it'll stay for now.
@register.filter
def role_for(forening, user):
    try:
        return forening_user_role(forening, user)
    except NoRoleRelationException:
        return ''
