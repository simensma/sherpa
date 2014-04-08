from django import template

register = template.Library()

@register.filter
def role_for(user, forening):
    """Return the role-code for a given users access to a given forening, or None if they don't have access"""
    for user_forening in user.all_foreninger():
        if user_forening == forening:
            return user_forening.role
    return None
