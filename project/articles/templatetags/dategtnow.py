from django import template
from datetime import datetime

register = template.Library()

def dategtnow(value):
    if(value is None):
        return False
    return value > datetime.now()
    
register.filter('dategtnow', dategtnow)