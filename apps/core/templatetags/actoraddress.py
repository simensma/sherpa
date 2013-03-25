from django import template

register = template.Library()

@register.filter
def actoraddress(actor):
    if actor.address.country == 'NO':
        if actor.address.a2 is None:
            formatted_a2 = ''
        else:
            formatted_a2 = ' (%s)' % actor.address.a2
        return "%s%s, %s %s" % (actor.address.a1, formatted_a2, actor.address.zipcode, actor.address.area)
    else:
        country = actor.address.get_country()
        formatted_a2 = ''
        if actor.address.a2 != '' and actor.address.a2 is not None:
            formatted_a2 = ', %s' % actor.address.a2
        formatted_a3 = ''
        if actor.address.a3 != '' and actor.address.a3 is not None:
            formatted_a3 = ', %s' % actor.address.a3
        return "%s%s%s (%s, %s)" % (actor.address.a1, formatted_a2, formatted_a3, country.name, country.code)
