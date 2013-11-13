# encoding: utf-8
from django import template

import json

register = template.Library()

@register.filter
def aktivitet_has_location(aktivitet, location):
    return location.id in json.loads(aktivitet.locations)
