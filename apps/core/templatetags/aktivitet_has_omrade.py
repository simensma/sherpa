# encoding: utf-8
from django import template

register = template.Library()

@register.filter
def aktivitet_has_omrade(aktivitet, omrade):
    return omrade.object_id in aktivitet.omrader
