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

    # Check if the organizer is a forening or a cabin
    if aktivitet_date.aktivitet.forening is not None:
        organizers_site = aktivitet_date.aktivitet.forening.get_homepage_site(prefetched=True)
        if organizers_site is not None and organizers_site.is_published:
            # The organizing forening's site is up and live, so go there
            return organizers_site

        # Their site isn't published, so just stay where we are
        return current_site

    elif aktivitet_date.aktivitet.forening_cabin is not None:
        # TODO: Return the homepage for this cabin, if created and published.
        # For now, just stay where we are.
        return current_site

    elif aktivitet_date.aktivitet.forening is None and aktivitet_date.aktivitet.forening_cabin is None:
        # Shouldn't happen, but throw an explicit exception just in case
        raise Exception("Shouldn't exist any aktivitet with no organizing forening NOR cabin")
