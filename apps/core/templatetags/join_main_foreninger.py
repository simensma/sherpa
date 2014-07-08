from django import template

register = template.Library()

@register.filter
def join_main_foreninger(forening, join_='og'):
    return (u' %s ' % join_).join([m.name for m in forening.get_main_forenings()])
