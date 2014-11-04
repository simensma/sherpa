import re

from django import template
from django.template.defaultfilters import striptags

register = template.Library()

@register.filter
def stripcomments(text):
    """Like Django's built-in striptags, but also removes HTML comments. The common use-case is IEs
    <!--[if gte mso 9]> ... <![endif]-->"""
    return striptags(re.sub('<!--.*?-->', '', text, flags=re.DOTALL))
