import re

from django import template

register = template.Library()

@register.filter
def menu_active(menu, request):
    url = re.sub('https?:\/\/', '', menu.url) # Strip protocol
    # Add final slash if missing
    if len(url) == 0 or url[-1] != '/':
        url = "%s/" % url
    return "%s%s" % (request.site.domain, request.path) == url
