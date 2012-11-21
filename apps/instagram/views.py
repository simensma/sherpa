from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
from django.template import RequestContext, loader

import requests, json

initial_url = 'https://api.instagram.com/v1/tags/turistforeningen/media/recent?client_id=%s' % settings.INSTAGRAM_CLIENT_ID

def index(request):
    r = requests.get(initial_url)
    data = json.loads(r.content)
    bulk = data['data']
    request.session['next_instagram_url'] = data['pagination']['next_url']
    context = {
        'bulk': bulk,
    }
    return render(request, 'instagram/index.html', context)

def more(request):
    r = requests.get(request.session['next_instagram_url'])
    data = json.loads(r.content)
    bulk = data['data']
    request.session['next_instagram_url'] = data['pagination']['next_url']
    t = loader.get_template('instagram/bulk.html')
    c = RequestContext(request, {'bulk': bulk})
    return HttpResponse(t.render(c))
