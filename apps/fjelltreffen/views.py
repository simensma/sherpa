# encoding: utf-8
from django.shortcuts import render
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied

from datetime import datetime, timedelta
from smtplib import SMTPException
import urllib
import json

from fjelltreffen.models import Annonse, get_annonser_by_filter
from core import validator
from sherpa25.models import Classified
from core.models import County
from focus.models import Actor
from user.models import Profile

#number of active annonser a user is allowed to have
ANNONSELIMIT = 5

default_min_age = 18
default_max_age = 200
default_fylke = '00'
default_gender = ''

def index(request):
    annonser, start_index = get_annonser_by_filter(default_min_age, default_max_age, default_fylke, default_gender)
    context = {
        'annonser':annonser,
        'start_index': start_index,
        'fylker':get_and_cache_fylker(),
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS}
    return render(request, 'main/fjelltreffen/index.html', context)

def load(request, start_index):
    annonsefilter = None
    try:
        annonsefilter = json.loads(request.POST['filter'])
        minage = int(annonsefilter['minage'])
        maxage = int(annonsefilter['maxage'])
        # Empty gender means both genders
        gender = annonsefilter['gender']
        fylke = annonsefilter['fylke']
    except (KeyError, ValueError) as e:
        minage = default_min_age
        maxage = default_max_age
        gender = default_gender
        fylke = default_fylke

    annonser, start_index = get_annonser_by_filter(minage, maxage, fylke, gender, int(start_index))

    context = RequestContext(request)
    context['annonser'] = annonser
    string = render_to_string('main/fjelltreffen/annonselist.html', context)
    return HttpResponse(json.dumps({
        'html': string,
        'start_index': start_index}))

@login_required
def edit(request, id):
    try:
        annonse = Annonse.objects.get(id=id)
        #checks if the user is the owner
        if annonse.profile != request.user.get_profile():
            raise PermissionDenied
    except Annonse.DoesNotExist:
        return render(request, 'main/fjelltreffen/edit_not_found.html')

    context = {
        'new': False,
        'annonse': annonse,
        'fylker': get_and_cache_fylker(),
        'requestedid': id,
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS}
    return render(request, 'main/fjelltreffen/edit.html', context)

@login_required
def new(request):
    if request.user.get_profile().get_actor() == None or not request.user.get_profile().get_actor().get_balance().is_payed():
        return render(request, 'main/fjelltreffen/payment_required.html')

    context = {
        'new': True,
        'annonse': None,
        'fylker': get_and_cache_fylker(),
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS}
    return render(request, 'main/fjelltreffen/edit.html', context)

@login_required
def delete(request, id):
    try:
        annonse = Annonse.objects.get(id=id);
        if annonse.profile != request.user.get_profile():
            #someone is trying to delete an annonse that dosent belong to them
            raise PermissionDenied
        else:
            annonse.delete()
            return HttpResponseRedirect(reverse('fjelltreffen.views.mine'))
    except Annonse.DoesNotExist:
        # Ignore - maybe a double-request, or something. They can try again if something failed.
        return HttpResponseRedirect(reverse('fjelltreffen.views.mine'))

def reply(request):
    try:
        content = json.loads(request.POST['reply'])
    except KeyError as e:
        return HttpResponse(status=400)

    try:
        replyid = content['id']
        replyname = content['name']
        replyemail = content['email']
        replytext = content['text']

        #validate input
        if validator.email(replyemail) and len(replyname) > 0 and len(replytext) > 5:

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

@login_required
def save(request):
    if request.user.get_profile().get_actor() == None:
        raise PermissionDenied

    # If user hasn't payed, allow editing, but not creating new annonser
    if not request.user.get_profile().get_actor().get_balance().is_payed() and request.POST['id'] == '':
        raise PermissionDenied

    if request.POST['id'] == '':
        # New annonse (not editing an existing one), create it
        annonse = Annonse()
        annonse.profile = request.user.get_profile()
    else:
        annonse = Annonse.objects.get(id=request.POST['id']);
        if annonse.profile != request.user.get_profile():
            #someone is trying to edit an annonse that dosent belong to them
            raise PermissionDenied

    annonse.fylke = County.objects.get(code=request.POST['fylke'])
    annonse.email = request.POST['email']
    annonse.title = request.POST['title']
    annonse.image = request.POST.get('image', '')
    annonse.text = request.POST['text']
    annonse.hidden = request.POST.get('hidden', '') == 'on'
    annonse.hideage = request.POST.get('hideage', '') == 'on'

    #validate input
    if validator.email(annonse.email) and len(annonse.title) > 0 and len(annonse.text) > 10:
        if not annonse.hidden:
            numposts = Annonse.objects.filter(profile=request.user.get_profile(), hidden=False).count()
            if(numposts > ANNONSELIMIT):
                #notify the user that he/she has too many active annonser
                return HttpResponse(json.dumps({'error':'toomany', 'num':ANNONSELIMIT}), status=400)
        annonse.save()
    else:
        return HttpResponse(status=400)

    return HttpResponseRedirect(reverse('fjelltreffen.views.mine'))

@login_required
def mine(request):
    #all annonser that belongs to the current user
    annonser = Annonse.objects.filter(profile=request.user.get_profile()).order_by('-timeadded')

    context = {'annonser': annonser}
    return render(request, 'main/fjelltreffen/mine.html', context)

def show(request, id):
    try:
        annonse = Annonse.objects.get(id=id, hidden=False)
    except (Annonse.DoesNotExist):
        annonse = None
    context = {'annonse': annonse, 'requestedid':id}
    return render(request, 'main/fjelltreffen/show.html', context)


#
# Utility methods
#

def get_and_cache_fylker():
    fylker = cache.get('annonse-fylker')
    if fylker == None:
        fylker = County.objects.all().order_by('name')
        cache.set('annonse-fylker', fylker, 60 * 60 *60)
    return fylker
