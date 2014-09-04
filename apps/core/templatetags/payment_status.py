from datetime import date

from django import template

register = template.Library()

@register.filter
def payment_status(user, prefix='Betalt,Ikke betalt'):
    """
    Outputs the user's payment status in text format. Could be done with template logic, but requires
    a fair amount of logic and it's a fairly typical pattern.
    TODO: Translate
    """

    prefix_paid, prefix_not_paid = prefix.split(',')

    today = date.today()
    current_year = today.year
    next_year = today.year + 1

    payment_status = user.get_payment_status()
    if user.is_lifelong_member():
        return '%s (livsvarig)'% (prefix_paid)
    elif payment_status == 'both':
        return '%s for %s, samt ut %s'% (prefix_paid, next_year, current_year)
    elif payment_status == 'current_not_next':
        return '%s ut %s, men ikke for %s' % (prefix_paid, current_year, next_year)
    elif payment_status == 'neither_years':
        return '%s for %s eller %s' % (prefix_not_paid, current_year, next_year)
    elif payment_status == 'current':
        return '%s for %s' % (prefix_paid, current_year)
    elif payment_status == 'not_this_year':
        return '%s for %s' % (prefix_not_paid, current_year)
    else:
        raise Exception("Unknown user payment_years status_code")
