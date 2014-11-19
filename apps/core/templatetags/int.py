from django import template

register = template.Library()

@register.filter
def int(value):
    # Explicit reference to the int() builtin since our int method overrides it in the namespace
    return __builtins__['int'](value)
