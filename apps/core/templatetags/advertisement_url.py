from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def advertisement_url(context, advertisement):
    if advertisement.id is not None:
        return u'http://%s%s' % (
            context['site'].domain,
            reverse('page.views.ad', args=[advertisement.id]),
        )
    else:
        return advertisement.destination_url()
