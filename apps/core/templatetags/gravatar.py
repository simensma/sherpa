from django import template

import md5

register = template.Library()

GRAVATAR_URL = "http://www.gravatar.com/avatar"

@register.simple_tag
def gravatar(email, size=40, default='mm'):
    hash = md5.new(email.strip().lower()).hexdigest()
    return "%s/%s?s=%s&d=%s" % (GRAVATAR_URL, hash, size, default)
