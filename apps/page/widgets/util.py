# encoding: utf-8
from datetime import datetime, date
import json

from django.core.cache import cache
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string

import requests

from admin.models import Campaign

from page.widgets.quote import QuoteWidget
from page.widgets.carousel import CarouselWidget
from page.widgets.articles import ArticlesWidget
from page.widgets.blog import BlogWidget
from page.widgets.embed import EmbedWidget
from page.widgets.fact import FactWidget
from page.widgets.button import ButtonWidget
from page.widgets.table import TableWidget
from page.widgets.campaign import CampaignWidget

WIDGETS = {
    'quote': QuoteWidget(),
    'carousel': CarouselWidget(),
    'articles': ArticlesWidget(),
    'blog': BlogWidget(),
    'embed': EmbedWidget(),
    'fact': FactWidget(),
    'button': ButtonWidget(),
    'table': TableWidget(),
    'campaign': CampaignWidget(),
}

def render_widget(request, widget_options, current_site, admin_context=False, raw=False, content_id=None):
    """Returns a string with the given widget rendered, ready for display.

    admin_context can be set to True to wrap the rendered widget in the appropriate container, and to tell
    the widget to display extra information to the admin-user if appropriate.

    raw can be set to True to exclude the containing element from the rendered html if
    the caller wants to handle that manually (typically when a widget is saved in the admin UI)

    content_id needs to be set if admin_context is True and raw is False as the admin container needs access
    to the content id
    """
    widget = parse_widget(request, widget_options, current_site)
    context = RequestContext(request, {
        'widget': widget,
        'admin_context': admin_context,
        'raw': raw,
        'content_id': content_id,
    })
    return render_to_string('common/widgets/container.html', context)

def parse_widget(request, widget_options, site):
    """
    Parse the supplied widget, perform the server-side view logic and return the final widget
    data context for rendering in its template
    """
    widget = WIDGETS[widget_options['widget']]
    data = widget.parse(widget_options, site)
    data.update({
        'json': json.dumps(widget_options),
        'template': 'common/widgets/%s/display.html' % widget_options['widget'],
        'widget': widget_options['widget'],
    })
    return data

def admin_context():
    """
    Returns a dict with data context for each widget which needs it in the admin-editor. Will be available in the
    editors through 'widget_data.<widget>'
    """
    return {widget_name: widget.admin_context() for widget_name, widget in WIDGETS.items()}

# Used temporary for static promo content
def get_static_promo_context(path):

    ROTATIONS = [
        {
            'id': 'final-vennetur',
            'name': '#vennetur',
            'start_date': date(year=2013, month=7, day=4),
            'end_date': date(year=2013, month=7, day=4),
        },
        {
            'id': '10-turer-pa-topp',
            'name': 'Klassikere',
            'start_date': date(year=2013, month=7, day=5),
            'end_date': date(year=2013, month=7, day=14),
        },
        {
            'id': 'bli-medlem',
            'name': 'Medlemskap',
            'start_date': date(year=2013, month=7, day=15),
            'end_date': date(year=2013, month=7, day=21),
        },
        {
            'id': 'hyttetur',
            'name': 'Hyttetur',
            'start_date': date(year=2013, month=7, day=22),
            'end_date': date(year=2013, month=7, day=28),
        },
        {
            'id': '10-turer-pa-topp',
            'name': 'Klassikere',
            'start_date': date(year=2013, month=7, day=29),
            'end_date': date(year=2013, month=8, day=11),
        },
        {
            'id': 'kom-deg-ut',
            'name': 'Kom deg ut',
            'start_date': date(year=2013, month=8, day=12),
            'end_date': date(year=2013, month=9, day=1),
        },
        {
            'id': 'fjellfilm',
            'name': 'Fjellfilm',
            'start_date': date(year=2013, month=9, day=2),
            'end_date': date(year=2013, month=9, day=14),
        },
        {
            'id': 'bli-medlem',
            'name': 'Medlemskap',
            'start_date': date(year=2013, month=9, day=15),
            'end_date': date(year=2013, month=9, day=15),
        },
        {
            'id': 'host',
            'name': 'Høst',
            'start_date': date(year=2013, month=9, day=16),
            'end_date': date(year=2013, month=10, day=10),
        },
        {
            'id': 'fotokonkurranse',
            'name': 'Fotokonkurranse',
            'start_date': date(year=2013, month=10, day=11),
            'end_date': date(year=2013, month=11, day=6),
        },
        {
            'id': 'gjensidige',
            'name': 'Medlemsfordeler',
            'start_date': date(year=2013, month=11, day=7),
            'end_date': date(year=2013, month=11, day=25),
        },
        {
            'id': 'stillenatur',
            'name': '#stillenatur',
            'start_date': date(year=2013, month=11, day=26),
            'end_date': date(year=2013, month=12, day=10),
        },
        {
            'id': 'gavemedlemskap',
            'name': 'Gavemedlemskap',
            'start_date': date(year=2013, month=12, day=11),
            'end_date': date(year=2013, month=12, day=18),
        },
        {
            'id': 'godjul',
            'name': 'God jul',
            'start_date': date(year=2013, month=12, day=19),
            'end_date': date(year=2013, month=12, day=31),
        },
        {
            'id': 'godtnyttar',
            'name': 'Godt nytt turår',
            'start_date': date(year=2014, month=1, day=1),
            'end_date': date(year=2014, month=1, day=12),
        },
        {
            'id': 'kom-deg-ut-feb',
            'name': 'Kom deg ut',
            'start_date': date(year=2014, month=1, day=13),
            'end_date': date(year=2014, month=2, day=2),
        },
        {
            'id': 'vintereventyr',
            'name': 'Vintereventyr',
            'start_date': date(year=2014, month=2, day=3),
            'end_date': date(year=2014, month=4, day=2),
        },
        {
            'id': 'pasketur',
            'name': 'Påsketur',
            'start_date': date(year=2014, month=4, day=3),
            'end_date': date(year=2014, month=4, day=23),
        },
        {
            'id': 'fotokonkurranse',
            'name': 'Fotokonkurranse',
            'start_date': date(year=2014, month=4, day=24),
            'end_date': date(year=2014, month=6, day=3),
        },
        {
            'id': 'sommer',
            'name': 'Sommer',
            'start_date': date(year=2014, month=6, day=4),
            'end_date': date(year=2014, month=6, day=19),
        },
        {
            'id': 'favoritthytter',
            'name': 'Favoritthytter',
            'start_date': date(year=2014, month=6, day=20),
            'end_date': date(year=2014, month=6, day=23),
        },
        {
            'id': 'sommerapning',
            'name': 'Sommeråpning',
            'start_date': date(year=2014, month=6, day=24),
            'end_date': date(year=2014, month=6, day=28),
        },
        {
            'id': 'favoritthytter',
            'name': 'Favoritthytter',
            'start_date': date(year=2014, month=6, day=29),
            'end_date': date(year=2014, month=6, day=29),
        },
    ]

    today = date.today()
    rotation_hits = [r for r in ROTATIONS if r['start_date'] <= today and r['end_date'] >= today]
    if len(rotation_hits) == 0:
        # No direct hits, pick the latest one from the past
        rotations_from_the_past = [r for r in ROTATIONS if r['end_date'] < today]
        rotation = max(rotations_from_the_past, key=lambda r: r['end_date'])
    elif len(rotation_hits) == 1:
        rotation = rotation_hits[0]
    else:
        raise Exception("There shouldn't be more than one rotation hits for any day, check the dates in your ROTATIONS list.")

    context = {}
    promos = [
        {'name': rotation['name'], 'url': '/', 'template': 'main', 'type': 'cover', 'rotation': rotation},
        {'name': 'Fellesturer', 'url': '/fellesturer/', 'template': 'fellesturer', 'type': 'default'},
        {'name': 'Hytter og ruter', 'url': '/hytter/', 'template': 'hytter', 'type': 'default'},
        {'name': 'Barn', 'url': '/barn/', 'template': 'barn', 'type': 'default'},
        {'name': 'Ungdom', 'url': '/ung/', 'template': 'ung', 'type': 'cover'},
        {'name': 'Fjellsport', 'url': '/fjellsport/', 'template': 'fjellsport', 'type': 'cover'},
        {'name': 'Senior', 'url': '/senior/', 'template': 'senior', 'type': 'default'},
        {'name': 'Skole', 'url': '/skole/', 'template': 'skole', 'type': 'default'},
        {'name': 'Kurs og utdanning', 'url': '/kurs/', 'template': 'kurs', 'type': 'default'},
        {'name': 'Tur for alle', 'url': '/tur-for-alle/', 'template': 'tur-for-alle', 'type': 'default'},
        {'name': 'Turplanlegger', 'url': '/utno/', 'template': 'ut', 'type': 'default'},
        {'name': 'Fjelltreffen', 'url': '/fjelltreffen/', 'type': 'direct'},
    ]

    for promo in promos:
        if path == promo['url'] and promo['type'] != 'direct':
            context['promo'] = {
                'template': 'common/widgets/promo/static/%s.html' % promo['template'],
                'type': promo.get('type'),
            }
            if 'rotation' in promo:
                context['promo'].update({
                    'rotation': promo['rotation'],
                    'rotation_template': 'common/widgets/promo/static/main-rotation/%s.html' % promo['rotation']['id'],
                })

    context['promos'] = promos

    return context
