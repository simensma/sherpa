from django import template

register = template.Library()

@register.filter
def gender(char):
    if char.lower() == 'm':
        return 'mann'
    elif char.lower() == 'f':
        return 'kvinne'
    else:
        return ''
