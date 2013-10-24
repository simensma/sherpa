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

    payment_years = user.get_payment_years()
    if payment_years['code'] == 'both':
        return '%s for %s, samt ut %s'% (prefix_paid, payment_years['next'], payment_years['current'])
    elif payment_years['code'] == 'current_not_next':
        return '%s ut %s, men ikke for %s' % (prefix_paid, payment_years['current'], payment_years['next'])
    elif payment_years['code'] == 'neither_years':
        return '%s for %s eller %s' % (prefix_not_paid, payment_years['current'], payment_years['next'])
    elif payment_years['code'] == 'current':
        return '%s for %s' % (prefix_paid, payment_years['current'])
    elif payment_years['code'] == 'not_this_year':
        return '%s for %s' % (prefix_not_paid, payment_years['current'])
    else:
        raise Exception("Unknown user payment_years code")
