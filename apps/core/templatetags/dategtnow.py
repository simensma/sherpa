from django import template
from datetime import datetime

register = template.Library()

@register.filter
def dategtnow(value):
    if(value is None):
        return False
    return value > datetime.now()
