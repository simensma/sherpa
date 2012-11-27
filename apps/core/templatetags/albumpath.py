from django import template

register = template.Library()

@register.filter
def albumpath(album):
    albums = [album]
    parent = album.parent
    while parent is not None:
        albums.insert(0, parent)
        parent = parent.parent
    return albums
