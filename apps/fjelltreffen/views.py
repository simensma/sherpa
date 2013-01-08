
from fjelltreffen.models import Annonse
from core.models import County
from django.shortcuts import render
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from datetime import datetime
from datetime import timedelta
from django.http import HttpResponse, Http404
import json
import urllib
from django.core.cache import cache

BULKLOADNUM = 20

defaultMinAge = 18
defaultMaxAge = 200
defaultFylke = 0
defaultGender = None

cachedQueries = []

def index(request):
    annonser = getAndCacheAnnonserByFilter(defaultMinAge, defaultMaxAge, defaultFylke, defaultGender)[0:BULKLOADNUM]

    context = {'annonser':annonser, 'fylker':getAndCacheFylker()}
    return render(request, 'main/fjelltreffen/index.html', context)

def load(request, page):
    annonsefilter = None
    try:
        annonsefilter = json.loads(request.POST['filter'])
        minage = int(annonsefilter.get('minage'))
        maxage = int(annonsefilter.get('maxage'))
        gender = annonsefilter.get('gender')
        fylke = int(annonsefilter.get('fylke'))
    except (JSONDecodeError, KeyError, ValueError) as e:
        minage = defaultMinAge
        maxage = defaultMaxAge
        gender = defaultGender
        fylke = defaultFylke

    page = int(page)
    A = BULKLOADNUM
    annonser = getAndCacheAnnonserByFilter(minage, maxage, fylke, gender)[(page*A):((page+1)*A)]

    context = RequestContext(request)
    context['annonser'] = annonser
    string = render_to_string('main/fjelltreffen/annonselist.html', context)
    return HttpResponse(json.dumps({'html':string}))

def getAndCacheFylker():
    fylker = cache.get('annonse-fylker')
    if fylker == None:
        fylker = County.objects.all().order_by('name')
        cache.set('annonse-fylker', fylker, 60 * 60)
    return fylker

def getAndCacheAnnonserByFilter(minage, maxage, fylke, gender):
    now = datetime.now();
    ninetydaysago = now - timedelta(days=90)
    #all annonser that are not hidden, is newer than 90 days, and matches the query, order by date

    cacheKey = 'fjelltreffenannonser' + str(minage) + str(maxage) + str(fylke) + str(gender)
    annonser = cache.get(cacheKey)
    if annonser == None:
        annonser = Annonse.objects.filter(hidden=False, age__gte=minage, age__lte=maxage, timeadded__gte=ninetydaysago)
        if gender != None:
            annonser = annonser.filter(gender=gender)
        if fylke != 0:
            annonser = annonser.filter(fylke=fylke)
        annonser = annonser.order_by('-timeadded')

        cache.set(cacheKey, annonser, 60 * 60)
        cachedQueries.append(cacheKey)
    return annonser

def edit(request, id):
    try:
        annonse = Annonse.objects.get(id=id)
        if annonse.userprofile != request.user.get_profile():
            annonse = None
    except Annonse.DoesNotExist:
        annonse = None
    context = {'new':False,'annonse':annonse,'fylker':getAndCacheFylker()}
    return render(request, 'main/fjelltreffen/new.html', context)

def new(request):
    context = {'new':True, 'annonse':None,'fylker':getAndCacheFylker()}
    return render(request, 'main/fjelltreffen/new.html', context)

def delete(request, id):
    try:
        annonse = Annonse.objects.get(id=id);
        if annonse.userprofile != request.user.get_profile():
            #someone is trying to delete an annonse that dosent belong to them
            return HttpResponse(500)   
        else:
            annonse.delete()
            return HttpResponse()
    except (Annonse.DoesNotExist, KeyError) as e:
        return HttpResponse(500)  

def save(request):
    try:
        content = json.loads(request.POST['annonse'])
    except (JSONDecodeError, KeyError) as e:
        return HttpResponse(500)

    try:
        id = content['id']
        annonse = Annonse.objects.get(id=id);
        if annonse.userprofile != request.user.get_profile():
            #someone is trying to edit an annonse that dosent belong to them
            print 'wrongusererror'
            return HttpResponse(500)          
    except (Annonse.DoesNotExist, KeyError) as e:
        print e
        annonse = Annonse()
        annonse.userprofile = request.user.get_profile()
    
    try:
        annonse.fylke = County.objects.get(code=content['fylke'])
    except (County.DoesNotExist, KeyError) as e:
        #could happen if the user tampers with the html to select an illegal county
        print e
        return HttpResponse(500)
    
    try:
        annonse.title = content['title']
        annonse.image = content.get('image')
        annonse.text = content['text']
        annonse.hidden = content['hidden']
        annonse.hideage = content['hideage']
        annonse.compute_age()
        annonse.compute_gender()
    except KeyError as e:
        print e
        return HttpResponse(500)
    annonse.save()
    
    #users want instant response, so cache is invalidated when an annonse is submitted
    #this should be alright, there is less than 1 new annonse being submitted pr hour on average
    for cacheKey in cachedQueries:
        cache.delete(cacheKey)

    return HttpResponse(json.dumps({'id':annonse.id, 'hidden':annonse.hidden}))

def mine(request):
    #alle annonser som tilhorer den aktive brukeren
    annonser = Annonse.objects.all()

    context = {'annonser': annonser}
    return render(request, 'main/fjelltreffen/mine.html', context)

def show(request, id):
    try:
        annonse = Annonse.objects.get(id=id)
    except (Annonse.DoesNotExist):
        annonse = None
    context = {'annonse': annonse}
    return render(request, 'main/fjelltreffen/show.html', context)

