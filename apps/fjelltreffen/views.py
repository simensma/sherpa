
from fjelltreffen.models import Annonse, invalidate_cache, getAndCacheAnnonserByFilter
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
from sherpa25.models import Classified
from django.conf import settings
from focus.models import Actor, BalanceHistory
from user.models import Profile

#number of active annonser a user is allowed to have
ANNONSELIMIT = 5

#annonser to load when a user requests more
BULKLOADNUM = 20

defaultMinAge = 18
defaultMaxAge = 200
defaultFylke = '00'
defaultGender = None

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
        cache.set('annonse-fylker', fylker, 60 * 60 *60)
    return fylker

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

#checks if the user has payed
#the result is  cached when the user has payed, but not when the user hasnt in case he/she pays because he/she want to use fjelltreffen
def has_payed(userprofile):
    #user has no focus user
    if userprofile.memberid == None:
        return False

    cachekey = 'fjelltreffen-haspayed'+str(userprofile.memberid)
    result = cache.get(cachekey)
    if result == None:
        try:
            #this should not be cached, when a user registers and payes whey would have to wait an hour to post
            actor = Actor.objects.get(memberid=userprofile.memberid)
            if actor == None:
                return False
            else:
                bills = BalanceHistory.objects.get(id=actor)
                result = bills.is_payed()
                if result == True:
                    cache.set(cachekey, result, 60 * 60)
        except (BalanceHistory.DoesNotExist, Actor.DoesNotExist) as e:
            return False
    return result

@login_required
def new(request):
    user = request.user.get_profile()
    context = {'new':True, 'annonse':None,'fylker':getAndCacheFylker(), 'user':user, 'haspayed':has_payed(user)}
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
                send_mail('DNT Fjelltreffen - Svar fra ' + replyname, replytext, replyemail, [replytoemail], fail_silently=False)
            except SMTPException as e:
                return HttpResponse(status=400)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
    except (Annonse.DoesNotExist, KeyError) as e:
        return HttpResponse(status=400)

def num_active_annonser(userprofile):
    return Annonse.objects.filter(userprofile=userprofile, hidden=False).count()

@login_required
def save(request):
    #a user that has not payed will not get access to the new-view, so this should not happen
    #if it does however, just deny the save
    if not has_payed(request.user.get_profile()):
        return HttpResponse(status=400)

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
    if email(annonse.email) and len(annonse.title) > 0 and len(annonse.text) > 10:
        if not annonse.hidden:
            if(num_active_annonser(request.user.get_profile()) > ANNONSELIMIT):
                #notify the user that he/she has too many active annonser
                print 'toomany'
                return HttpResponse(json.dumps({'error':'toomany', 'num':ANNONSELIMIT}), status=400)
        annonse.save()
        #users want instant response, so cache is invalidated when an annonse is submitted
        #this should be alright, there is less than 1 new annonse being submitted pr hour on average
        invalidate_cache()
    else:
        return HttpResponse(status=400)

    return HttpResponse(json.dumps({'id':annonse.id}))

@login_required
def mine(request):
    #all annonser that belongs to the current user
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

