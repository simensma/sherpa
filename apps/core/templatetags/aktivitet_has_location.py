# encoding: utf-8
import json

from django import template

register = template.Library()

@register.filter
def aktivitet_has_location(aktivitet, location):
    return location.id in json.loads(aktivitet.locations)
