from django import template

register = template.Library()

@register.filter
def aktivitet_destination(aktivitet_date, request):
    """Links to an aktivitet should in principle send the user to the site of the arranging forening, with a few
    exceptions; all defined here."""

    current_site = request.site
    current_forening = current_site.forening

    if current_site.type == 'forening' and ( \
            current_forening == aktivitet_date.aktivitet.forening or
            current_forening in aktivitet_date.aktivitet.co_foreninger.all()):
        # The current site is one of the arranging foreninger, so we can stay on this site
        return current_site

    arranging_site = aktivitet_date.aktivitet.forening.get_homepage_site(prefetched=True)
    if arranging_site is not None and arranging_site.is_published:
        # The arranging forening's site is up and live, so go there
        return arranging_site

    # Their site isn't published, so just stay wherever we are
    return current_site
