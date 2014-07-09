from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    updated = context['request'].GET.copy()
    for key in kwargs:
        if updated.get(key):
            updated.pop(key)

        if kwargs[key] != '':
            updated.__setitem__(key, kwargs[key])
    return updated.urlencode()

