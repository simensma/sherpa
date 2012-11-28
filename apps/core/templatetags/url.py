from django import template
from django.template.defaulttags import url as django_url
from django.template.base import Node

import md5

register = template.Library()

class PathURLNode(Node):
    def __init__(self, urlnode):
        self.urlnode = urlnode

    def render(self, context):
        prefix = context['site'].prefix
        return '%s%s' % ('/%s' % prefix if prefix != '' else '', self.urlnode.render(context))

@register.tag
def url(parser, token):
    return PathURLNode(django_url(parser, token))
