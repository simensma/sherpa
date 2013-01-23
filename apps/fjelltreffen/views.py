# encoding: utf-8
from django.shortcuts import render
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
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
default_max_age = '' # No limit - empty string is also used in the select box
default_county = '00'
default_gender = ''

#
# Public views
#

def index(request):
    annonser, start_index = get_annonser_by_filter(default_min_age, default_max_age, default_county, default_gender)
    context = {
        'annonser':annonser,
        'start_index': start_index,
        'counties':County.typical_objects().order_by('name'),
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS,
        'age_limits': settings.FJELLTREFFEN_AGE_LIMITS}
    return render(request, 'main/fjelltreffen/index.html', context)

def load(request, start_index):
    annonsefilter = None
    try:
        annonsefilter = json.loads(request.POST['filter'])
        minage = annonsefilter['minage']
        maxage = annonsefilter['maxage']
        # Empty gender means both genders
        gender = annonsefilter['gender']
        county = annonsefilter['county']
    except (KeyError, ValueError) as e:
        minage = default_min_age
        maxage = default_max_age
        gender = default_gender
        county = default_county

    annonser, start_index = get_annonser_by_filter(minage, maxage, county, gender, int(start_index))

    context = RequestContext(request)
    context['annonser'] = annonser
    string = render_to_string('main/fjelltreffen/annonselist.html', context)
    return HttpResponse(json.dumps({
        'html': string,
        'start_index': start_index}))

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

def show(request, id):
    try:
        annonse = Annonse.objects.get(id=id, hidden=False)
    except (Annonse.DoesNotExist):
        annonse = None
    context = {'annonse': annonse, 'requestedid':id}
    return render(request, 'main/fjelltreffen/show.html', context)


#
# Actions for logged-in users (crud)
#

@login_required
@user_passes_test(lambda u: u.get_profile().memberid is not None, login_url='/minside/registrer-medlemskap/')
def new(request):
    if not request.user.get_profile().get_actor().get_balance().is_payed():
        return render(request, 'main/fjelltreffen/payment_required.html')

    if Annonse.objects.filter(profile=request.user.get_profile(), hidden=False).count() >= ANNONSELIMIT:
        context = {'active_annonse_limit': ANNONSELIMIT}
        return render(request, 'main/fjelltreffen/too_many_active_annonser.html', context)

    context = {
        'counties': County.typical_objects().order_by('name'),
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS,
        'active_annonse_limit': ANNONSELIMIT}
    return render(request, 'main/fjelltreffen/edit.html', context)

@login_required
@user_passes_test(lambda u: u.get_profile().memberid is not None, login_url='/minside/registrer-medlemskap/')
def edit(request, id):
    try:
        annonse = Annonse.objects.get(id=id)
        #checks if the user is the owner
        if annonse.profile != request.user.get_profile():
            raise PermissionDenied
    except Annonse.DoesNotExist:
        return render(request, 'main/fjelltreffen/edit_not_found.html')

    context = {
        'annonse': annonse,
        'counties': County.typical_objects().order_by('name'),
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS,
        'active_annonse_limit': ANNONSELIMIT}
    return render(request, 'main/fjelltreffen/edit.html', context)

@login_required
@user_passes_test(lambda u: u.get_profile().memberid is not None, login_url='/minside/registrer-medlemskap/')
def save(request):
    if request.user.get_profile().get_actor() == None:
        raise PermissionDenied

    # If user hasn't payed, allow editing, but not creating new annonser
    if not request.user.get_profile().get_actor().get_balance().is_payed() and request.POST['id'] == '':
        raise PermissionDenied

    # Pre-save validations
    errors = False

    if request.POST['id'] == '':
        # New annonse (not editing an existing one), create it
        annonse = Annonse()
        annonse.profile = request.user.get_profile()
    else:
        annonse = Annonse.objects.get(id=request.POST['id']);
        if annonse.profile != request.user.get_profile():
            #someone is trying to edit an annonse that dosent belong to them
            raise PermissionDenied

    if request.POST['title'] == '':
        messages.error(request, 'missing_title')
        errors = True

    if not validator.email(request.POST['email']):
        messages.error(request, 'invalid_email')
        errors = True

    if request.POST['text'] == '':
        messages.error(request, 'missing_text')
        errors = True

    if errors:
        if request.POST['id'] == '':
            return HttpResponseRedirect(reverse('fjelltreffen.views.new'))
        else:
            return HttpResponseRedirect(reverse('fjelltreffen.views.edit', args=[request.POST['id']]))

    # Override any attempt to show a hidden annonse when the user hasn't payed
    if annonse.hidden and not request.user.get_profile().get_actor().get_balance().is_payed():
        hidden = True
    else:
        hidden = request.POST.get('hidden', '') == 'on'

    annonse.county = County.objects.get(code=request.POST['county'])
    annonse.email = request.POST['email']
    annonse.title = request.POST['title']
    annonse.image = request.POST.get('image', '')
    annonse.text = request.POST['text']
    annonse.hidden = hidden
    annonse.hideage = request.POST.get('hideage', '') == 'on'

    # Post-save validations, to potentially keep some of the input
    redirect_back = False

    # Hide the annonse if user has more active annonser than the limit
    if not hidden and Annonse.objects.filter(profile=request.user.get_profile(), hidden=False).count() >= ANNONSELIMIT:
        messages.error(request, 'too_many_active_annonser')
        annonse.hidden = True
        redirect_back = True

    annonse.save()

    if redirect_back:
        if request.POST['id'] == '':
            # Note: The user doesn't get access to the 'new' view, so this shouldn't happen, but potentially, the user
            # can make POST requests to *this* view, so just handle the case anyway.
            return HttpResponseRedirect(reverse('fjelltreffen.views.new'))
        else:
            return HttpResponseRedirect(reverse('fjelltreffen.views.edit', args=[request.POST['id']]))
    else:
        return HttpResponseRedirect(reverse('fjelltreffen.views.mine'))

@login_required
@user_passes_test(lambda u: u.get_profile().memberid is not None, login_url='/minside/registrer-medlemskap/')
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

@login_required
@user_passes_test(lambda u: u.get_profile().memberid is not None, login_url='/minside/registrer-medlemskap/')
def mine(request):
    #all annonser that belongs to the current user
    annonser = Annonse.objects.filter(profile=request.user.get_profile()).order_by('-timeadded')

    context = {'annonser': annonser}
    return render(request, 'main/fjelltreffen/mine.html', context)
