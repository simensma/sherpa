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
from page.widgets.aktivitet_listing import AktivitetListingWidget
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
    'aktivitet_listing': AktivitetListingWidget(),
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

def admin_context(site):
    """
    Returns a dict with data context for each widget which needs it in the admin-editor. Will be available in the
    editors through 'widget_data.<widget>'
    """
    return {widget_name: widget.admin_context(site) for widget_name, widget in WIDGETS.items()}
