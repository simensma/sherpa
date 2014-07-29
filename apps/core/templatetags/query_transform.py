from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    updated = context['request'].GET.copy()
    for key, value in kwargs.items():
        if updated.get(key):
            updated.pop(key)

        if value != '':
            updated[key] = value
    return updated.urlencode()

