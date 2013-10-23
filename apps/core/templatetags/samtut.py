from django import template

register = template.Library()

@register.filter
def samtut(membership_year_date_set):
    """
    This filter is used for text formatting, which could be done with template logic but it requires
    a fair amount of logic and it's a fairly typical pattern.
    TODO: Translate
    """
    if membership_year_date_set['has_passed']:
        return '%s, samt ut %s' % (membership_year_date_set['date'].year + 1, membership_year_date_set['date'].year)
    else:
        return '%s' % membership_year_date_set['date'].year
