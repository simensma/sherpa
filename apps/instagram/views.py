from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
from django.template import RequestContext, loader
from django.core.cache import cache

import requests, json

initial_url = 'https://api.instagram.com/v1/tags/turistforeningen/media/recent?client_id=%s' % settings.INSTAGRAM_CLIENT_ID

def index(request):
    data = cache.get('instagram.url.%s' % initial_url)
    if data == None:
        r = requests.get(initial_url)
        data = json.loads(r.content)
        cache.set('instagram.url.%s' % initial_url, data, 60 * 60)

    bulk = data['data']
    request.session['next_instagram_url'] = data['pagination']['next_url']
    context = {
        'bulk': bulk,
    }
    return render(request, 'instagram/index.html', context)

def more(request):
    data = cache.get('instagram.url.%s' % request.session['next_instagram_url'])
    if data == None:
        r = requests.get(request.session['next_instagram_url'])
        data = json.loads(r.content)
        cache.set('instagram.url.%s' % request.session['next_instagram_url'], data, 60 * 60)

    bulk = data['data']
    meta = {}
    if not 'next_url' in data['pagination']:
        meta['end'] = True
        del request.session['next_instagram_url']
    else:
        request.session['next_instagram_url'] = data['pagination']['next_url']
    t = loader.get_template('instagram/bulk.html')
    c = RequestContext(request, {'bulk': bulk})
    return HttpResponse(json.dumps({'content': t.render(c), 'meta': meta}))
