from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
from django.template import RequestContext, loader
from django.core.cache import cache

import requests, json

initial_url = 'https://api.instagram.com/v1/tags/turistforeningen/media/recent?client_id=%s' % settings.INSTAGRAM_CLIENT_ID

def index(request):
    if not 'instagram' in request.session:
        request.session['instagram'] = {}

    data = cache.get('instagram.url.%s' % initial_url)
    if data is None:
        r = requests.get(initial_url)
        data = json.loads(r.content)
        cache.set('instagram.url.%s' % initial_url, data, 60 * 60)

    # Still assuming 18 items
    bulk = data['data']
    request.session['instagram']['iteration'] = 0
    request.session['instagram']['next_url'] = data['pagination']['next_url']
    context = {
        'bulk': bulk,
    }
    request.session.modified = True
    return render(request, 'instagram/index.html', context)

def more(request):
    data = cache.get('instagram.url.%s' % request.session['instagram']['next_url'])
    if data is None:
        r = requests.get(request.session['instagram']['next_url'])
        data = json.loads(r.content)
        cache.set('instagram.url.%s' % request.session['instagram']['next_url'], data, 60 * 60)

    items = [next_image(request, item) for item in data['data']]
    meta = {}
    if not 'next_url' in data['pagination']:
        meta['end'] = True
        del request.session['instagram']['next_url']
    else:
        request.session['instagram']['next_url'] = data['pagination']['next_url']
    request.session.modified = True
    return HttpResponse(json.dumps({'items': items, 'meta': meta}))

iterations = ['small', 'small', 'small', 'small', 'medium', 'large', 'medium', 'small', 'small', 'small', 'small', 'medium', 'medium', 'medium', 'medium', 'small', 'small', 'large']
def next_image(request, item):
    t = loader.get_template('instagram/image_%s.html' % iterations[request.session['instagram']['iteration']])
    c = RequestContext(request, {'item': item})
    request.session['instagram']['iteration'] += 1
    if request.session['instagram']['iteration'] == len(iterations):
        request.session['instagram']['iteration'] = 0
    return t.render(c)
