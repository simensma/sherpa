from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    updated = context['request'].GET.copy()
    updated.update(kwargs)
    return updated.urlencode()

