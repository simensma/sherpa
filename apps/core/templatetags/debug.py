from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def debug(tags):
    return settings.DEBUG
