
from fjelltreffen.models import Annonse
from core.models import County
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime
from datetime import timedelta
from django.http import HttpResponse, Http404
import json
import urllib
from django.core.cache import cache

NUM_ANNONSER_TO_DISPLAY = 15

def index(request):
    
    now = datetime.now();
    ninetydaysago = now - timedelta(days=90)
    #all annonser that are not hidden og is newer than 90 days, order by date
    annonser = Annonse.objects.filter(hidden=False, timeadded__gte=ninetydaysago).order_by('-timeadded')
    #annonser = Annonse.objects.all()
    print annonser

    context = {'annonser': annonser}
    return render(request, 'main/fjelltreffen/index.html', context)

def getAndCacheFylker():
    fylker = cache.get('annonse-fylker')
    if fylker == None:
        fylker = County.objects.all().order_by('name')
        cache.set('annonse-fylker', fylker, 60 * 60)
    return fylker

def new(request):
    context = {'annonse':None,'fylker':getAndCacheFylker()}
    return render(request, 'main/fjelltreffen/new.html', context)

def delete(request, id):
    try:
        annonse = Annonse.objects.get(id=content['id']);
        if annonse.userprofile != request.user.get_profile():
            #someone is trying to delete an annonse that dosent belong to them
            return HttpResponse(500)   
        else:
            annonse.delete       
    except (Annonse.DoesNotExist, KeyError) as e:
        return HttpResponse(500)   

def save(request):
    try:
        content = json.loads(urllib.unquote_plus(request.POST['annonse']))
    except (JSONDecodeError, KeyError) as e:
        return HttpResponse(500)

    print content
    #return HttpResponse()

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
        annonse.compute_age()
        annonse.compute_gender()
    except KeyError as e:
        print e
        return HttpResponse(500)
    annonse.save()
    print 'saved'

    return HttpResponse(json.dumps({'id':annonse.id, 'hidden':annonse.hidden}))

def new_edit_annonse(request, id):
    try:
        annonse = Annonse.objects.get(id=id)
    except (Annonse.DoesNotExist):
        annonse = None
    context = {'annonse':annonse,}
    return render(request, 'main/fjelltreffen/edit.html', context)



def mine(request):
    #alle annonser som tilhorer den aktive brukeren
    annonser = Annonse.objects.all()

    context = {'annonser': annonser}
    return render(request, 'main/fjelltreffen/mine.html', context)

def single(request, id):
    try:
        annonse = Annonse.objects.get(id=id)
    except (Annonse.DoesNotExist):
        annonse = None
        #raise Http404
    context = {'annonse': annonse}
    return render(request, 'main/fjelltreffen/single.html', context)

