# encoding: utf-8
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string

import json

from admin.models import Image, Album

from admin.images.views import parse_objects, list_parents

def content_dialog(request):
    album = request.POST['album']
    if album == '':
        objects = parse_objects([], Album.objects.filter(parent=None).order_by('name'), [])
    else:
        current_album = Album.objects.get(id=album)
        objects = parse_objects(list_parents(current_album),
            Album.objects.filter(parent=album).order_by('name'),
            Image.objects.filter(album=album))

    context = RequestContext(request, {
        'parents': objects['parents'],
        'albums': objects['albums'],
        'albums_divided': divide_for_three_columns(objects['albums']),
        'images': objects['images'],
        'no_results_message': '<strong>Her var det tomt!</strong><br>Det er ingen album eller bilder i dette albumet.'
        })
    return HttpResponse(json.dumps({'html': render_to_string('common/admin/images/util/image-archive-picker-content.html', context)}))

def search_dialog(request):
    images = []
    if len(request.POST['query']) >= settings.IMAGE_SEARCH_LENGTH:
        # TODO: Should search (programmatically) for uploader name/email
        # These might be in our DB or in Focus.
        for word in request.POST['query'].split(' '):
            images += Image.objects.filter(
                Q(description__icontains=word) |
                Q(album__name__icontains=word) |
                Q(photographer__icontains=word) |
                Q(credits__icontains=word) |
                Q(licence__icontains=word) |
                Q(exif__icontains=word) |
                Q(tags__name__icontains=word)
        )
    objects = parse_objects([], [], images)

    context = RequestContext(request, {
        'parents': objects['parents'],
        'albums': objects['albums'],
        'albums_divided': divide_for_three_columns(objects['albums']),
        'images': objects['images'],
        'no_results_message': '<strong>Beklager!</strong><br>Vi fant ingen bilder tilsvarende søket ditt :-('
        })
    return HttpResponse(json.dumps({'html': render_to_string('common/admin/images/util/image-archive-picker-content.html', context)}))

# Lol, I bet there's a much easier way to do this, but whatever, this works for now.
def divide_for_three_columns(albums):
    bulk = len(albums) / 3
    rest = len(albums) % 3

    if rest > 0:
        first = bulk + 1
        rest -= 1
    else:
        first = bulk

    if rest > 0:
        second = first + bulk + 1
    else:
        second = first + bulk

    return [albums[:first], albums[first:second], albums[second:]]
