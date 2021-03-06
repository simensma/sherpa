from itertools import cycle, islice
import json
import logging
import sys

from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template import RequestContext, loader
from django.core.cache import cache

import requests

from page.models import AdPlacement
from instagram.exceptions import InstagramServerError

logger = logging.getLogger('sherpa')

initial_url = 'https://api.instagram.com/v1/tags/%s/media/recent?client_id=%s'

def default(request):
    tags = ['turistforeningen', 'komdegut']
    request.session['instagram'] = {
        'iteration': 0,
        'tags': {x: initial_url % (x, settings.INSTAGRAM_CLIENT_ID) for x in tags}
    }
    return render(request, 'central/instagram/default.html')

def opptur2013(request):
    tags = ['opptur2013']
    request.session['instagram'] = {
        'iteration': 0,
        'tags': {x: initial_url % (x, settings.INSTAGRAM_CLIENT_ID) for x in tags}
    }
    return render(request, 'central/instagram/opptur.html')

def load(request):
    if not 'instagram' in request.session:
        return redirect('instagram.views.index')
    try:
        meta = {}
        item_lists = []
        for tag, next_url in request.session['instagram']['tags'].items():
            if next_url is None:
                # This one didn't have a next_url on its last request
                continue

            data = cache.get('instagram.url.%s' % next_url)
            if data is None:
                r = requests.get(next_url)
                if r.status_code != 200:
                    raise InstagramServerError(r)
                data = json.loads(r.content)
                cache.set('instagram.url.%s' % next_url, data, 60 * 60)
            item_lists.append([item for item in data['data']])

            if not 'next_url' in data['pagination']:
                request.session['instagram']['tags'][tag] = None
            else:
                request.session['instagram']['tags'][tag] = data['pagination']['next_url']

        # If there are no more 'next_url's, there are no more picturs for any tags
        if all([x is None for x in request.session['instagram']['tags'].values()]):
            meta['end'] = True

        # Merge the photos, and then render the appropriate template
        items = list(roundrobin(*item_lists))
        items = [next_image(request, item) for item in items]

        request.session.modified = True
        return HttpResponse(json.dumps({'items': items, 'meta': meta}))
    except InstagramServerError as e:
        logger.warning(u"Instagram returnerte ikke 200 OK ved request",
            exc_info=sys.exc_info(),
            extra={
                'instagram_request': e.instagram_request,
                'response_text': e.instagram_request.text
            }
        )
        return HttpResponse(json.dumps({'status': 'instagram_server_error'}))

iterations = ['small', 'small', 'small', 'small', 'medium', 'large', 'medium', 'small', 'small', 'small', 'small', 'medium', 'medium', 'medium', 'medium', 'small', 'small', 'large']
def next_image(request, item):
    t = loader.get_template('central/instagram/images/%s.html' % iterations[request.session['instagram']['iteration']])
    c = RequestContext(request, {'item': item})
    request.session['instagram']['iteration'] += 1
    if request.session['instagram']['iteration'] == len(iterations):
        request.session['instagram']['iteration'] = 0
    return t.render(c)

def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))
