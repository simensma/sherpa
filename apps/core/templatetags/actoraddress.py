from django import template

register = template.Library()

@register.filter
def actoraddress(actor):
    if actor.address.a2 is None:
        formatted_a2 = ''
    else:
        formatted_a2 = ' (%s)' % actor.address.a2
    return "%s%s, %s %s" % (actor.address.a1, formatted_a2, actor.address.zipcode, actor.address.area)
