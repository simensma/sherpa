
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
from django.core.mail import send_mail
from smtplib import SMTPException
from core.validator import email

BULKLOADNUM = 20

defaultMinAge = 18
defaultMaxAge = 200
defaultFylke = '00'
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
        minage = int(annonsefilter['minage'])
        maxage = int(annonsefilter['maxage'])
        #gender can be undefined, should then return none for no gender-filter
        gender = annonsefilter.get('gender')
        fylke = annonsefilter['fylke']
    except (KeyError, ValueError) as e:
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
        if fylke != '00':
            annonser = annonser.filter(fylke__code=fylke)
        annonser = annonser.order_by('-timeadded')

        cache.set(cacheKey, annonser, 60 * 60)
        cachedQueries.append(cacheKey)
    return annonser

@login_required
def edit(request, id):
    try:
        annonse = Annonse.objects.get(id=id)
        if annonse.userprofile != request.user.get_profile():
            annonse = None
    except Annonse.DoesNotExist:
        annonse = None
    context = {'new':False,'annonse':annonse,'fylker':getAndCacheFylker(), 'requestedid':id}
    return render(request, 'main/fjelltreffen/new.html', context)

@login_required
def new(request):
    user = request.user.get_profile()
    context = {'new':True, 'annonse':None,'fylker':getAndCacheFylker(), 'user':user}
    return render(request, 'main/fjelltreffen/new.html', context)

@login_required
def delete(request, id):
    try:
        annonse = Annonse.objects.get(id=id);
        if annonse.userprofile != request.user.get_profile():
            #someone is trying to delete an annonse that dosent belong to them
            return HttpResponse(status=400)   
        else:
            annonse.delete()
            return HttpResponse()
    except (Annonse.DoesNotExist, KeyError) as e:
        return HttpResponse(status=400)

def reply(request):
    try:
        content = json.loads(request.POST['reply'])
        print content
    except KeyError as e:
        print 'mail5001'
        return HttpResponse(status=400)

    try:
        replyid = content['id']
        replyname = content['name']
        replyemail = content['email']
        replytext = content['text']

        #validate input
        if email(replyemail) and len(replyname) > 0 and len(replytext) > 5:
            
            replytoemail = Annonse.objects.get(id=replyid).email
            try:
                send_mail('DNT Fjelltreffen - Svar fra ' + replyname, replytext, replyemail, ['eidheim@live.no'], fail_silently=False)    
            except SMTPException as e:
                return HttpResponse(status=400)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
    except (Annonse.DoesNotExist, KeyError) as e:
        return HttpResponse(status=400)

@login_required
def save(request):
    try:
        content = json.loads(request.POST['annonse'])
    except KeyError as e:
        return HttpResponse(status=400)

    try:
        id = content['id']
        annonse = Annonse.objects.get(id=id);
        if annonse.userprofile != request.user.get_profile():
            #someone is trying to edit an annonse that dosent belong to them
            return HttpResponse(status=400)
    except (Annonse.DoesNotExist, KeyError) as e:
        #the user is creating a new annonse, not editing an excisting one
        annonse = Annonse()
        annonse.userprofile = request.user.get_profile()
    
    try:
        annonse.fylke = County.objects.get(code=content['fylke'])
    except (County.DoesNotExist, KeyError) as e:
        #could happen if the user tampers with the html to select an illegal county
        return HttpResponse(status=400)
    
    try:
        annonse.email = content['email']
        annonse.title = content['title']
        annonse.image = content.get('image')
        annonse.text = content['text']
        annonse.hidden = content['hidden']
        annonse.hideage = content['hideage']
        annonse.compute_age()
        annonse.compute_gender()
    except KeyError as e:
        #something is missing in the data sendt
        return HttpResponse(status=400)

    #validate input
    if email(annonse.email) and len(str.strip(annonse.title)) > 0 and len(str.strip(annonse.text)) > 10:
        annonse.save()
    else:
        return HttpResponse(status=400)
    
    #users want instant response, so cache is invalidated when an annonse is submitted
    #this should be alright, there is less than 1 new annonse being submitted pr hour on average
    for cacheKey in cachedQueries:
        cache.delete(cacheKey)

    return HttpResponse(json.dumps({'id':annonse.id}))

@login_required
def mine(request):
    #alle annonser som tilhorer den aktive brukeren
    annonser = Annonse.objects.filter(userprofile=request.user.get_profile()).order_by('-timeadded')

    context = {'annonser': annonser}
    return render(request, 'main/fjelltreffen/mine.html', context)

def show(request, id):
    try:
        annonse = Annonse.objects.get(id=id, hidden=False)
    except (Annonse.DoesNotExist):
        annonse = None
    context = {'annonse': annonse, 'requestedid':id}
    return render(request, 'main/fjelltreffen/show.html', context)

