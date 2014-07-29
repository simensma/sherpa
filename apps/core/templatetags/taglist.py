import json

from django import template

register = template.Library()

@register.filter
def taglist(tags):
    return json.dumps([tag.name for tag in tags])
