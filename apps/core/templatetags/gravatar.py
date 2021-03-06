import md5

from django import template

register = template.Library()

GRAVATAR_URL = "https://www.gravatar.com/avatar"

@register.simple_tag
def gravatar(email, size=40, default='mm'):
    hash = md5.new(email.strip().lower()).hexdigest()
    return "%s/%s?s=%s&d=%s" % (GRAVATAR_URL, hash, size, default)
