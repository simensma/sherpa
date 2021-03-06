from datetime import date

from django import template

register = template.Library()

@register.filter
def payment_status(user, prefix='Medlem,Ikke medlem'):
    """
    Outputs the user's payment status in text format. Could be done with template logic, but requires
    a fair amount of logic and it's a fairly typical pattern.
    TODO: Translate
    """

    prefix_paid, prefix_not_paid = prefix.split(',')

    today = date.today()
    current_year = today.year
    next_year = today.year + 1

    status = user.get_payment_status()
    if user.is_lifelong_member():
        return '%s (livsvarig)'% (prefix_paid)

    if status['new_membership_year']:
        if status['current_year'] and status['next_year']:
            return '%s ut %s, samt hele %s' % (prefix_paid, current_year, next_year)
        elif status['current_year'] and not status['next_year']:
            return '%s ut %s, men ikke %s' % (prefix_paid, current_year, next_year)
        elif not status['current_year'] and status['next_year']:
            raise Exception("Illegal state: current_year should always be paid when next_year is. Go debug!")
        elif not status['current_year'] and not status['next_year']:
            return '%s %s eller %s' % (prefix_not_paid, current_year, next_year)
    else:
        if status['current_year']:
            return '%s %s' % (prefix_paid, current_year)
        else:
            return '%s %s' % (prefix_not_paid, current_year)
