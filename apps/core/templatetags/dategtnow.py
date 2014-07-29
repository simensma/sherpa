from datetime import datetime

from django import template

register = template.Library()

@register.filter
def dategtnow(value):
    if(value is None):
        return False
    return value > datetime.now()
