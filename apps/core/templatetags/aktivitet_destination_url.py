from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def aktivitet_destination_url(context, aktivitet_date):
    """Links to an aktivitet should in principle send the user to the site of the arranging forening, with a few
    exceptions; all defined here."""

    url_path = reverse('aktiviteter.views.show', args=[aktivitet_date.id])

    current_site = context['request'].site
    if current_site.type == 'forening' and ( \
            current_site.forening == aktivitet_date.aktivitet.forening or
            current_site.forening in aktivitet_date.aktivitet.co_foreninger.all()):
        # The current site is one of the arranging foreninger, so we can stay on this site
        # Just return the relative path
        return url_path

    arranging_site = aktivitet_date.aktivitet.forening.get_homepage_site(prefetched=True)
    if arranging_site is not None and arranging_site.is_published:
        # The arranging forening's site is up and live, so go there
        return 'http://%s%s' % (arranging_site.domain, url_path)

    # Their site isn't published, so just stay wherever we are
    return url_path
