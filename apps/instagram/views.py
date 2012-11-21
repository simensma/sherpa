from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings

import requests, json

initial_url = 'https://api.instagram.com/v1/tags/turistforeningen/media/recent?client_id=%s' % settings.INSTAGRAM_CLIENT_ID

def index(request):
    r = requests.get(initial_url)
    data = json.loads(r.content)
    images = [i['images'] for i in data['data']]
    bulk = images[0:6]
    context = {
        'images': images,
        'bulk': bulk,
    }
    return render(request, 'instagram/index.html', context)
