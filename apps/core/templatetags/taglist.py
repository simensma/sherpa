from django import template

import json

register = template.Library()

@register.filter
def taglist(tags):
    return json.dumps([tag.name for tag in tags])
