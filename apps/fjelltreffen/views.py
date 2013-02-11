# encoding: utf-8
from django.shortcuts import render
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied

from datetime import date, timedelta
import json
import sys
import logging

from sherpa.decorators import user_requires, user_requires_login
from fjelltreffen.models import Annonse
from fjelltreffen.forms import ReplyForm, ReplyAnonForm
from core import validator
from core.models import County

logger = logging.getLogger('sherpa')

#
# Public views
#

def index(request):
    annonser, start_index, end = Annonse.get_by_filter(request.session.get('fjelltreffen.filter', {}))
    context = {
        'annonser': annonser,
        'start_index': start_index,
        'end': end,
        'counties': County.typical_objects().order_by('name'),
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS,
        'age_limits': settings.FJELLTREFFEN_AGE_LIMITS,
        'filter': request.session.get('fjelltreffen.filter')}
    return render(request, 'main/fjelltreffen/index.html', context)

def load(request, start_index):
    if not request.is_ajax() or request.method != 'POST':
        raise PermissionDenied

    filter = json.loads(request.POST['filter'])

    request.session['fjelltreffen.filter'] = {
            'minage': filter['minage'],
            'maxage': filter['maxage'],
            'gender': filter['gender'], # Empty gender means both genders
            'county': filter['county'],
            'text': filter['text']}

    annonser, start_index, end = Annonse.get_by_filter(request.session['fjelltreffen.filter'], int(start_index))

    context = RequestContext(request)
    context['annonser'] = annonser
    string = render_to_string('main/fjelltreffen/annonselist.html', context)
    return HttpResponse(json.dumps({
        'html': string,
        'start_index': start_index,
        'end': end}))

def show(request, id):
    try:
        annonse = Annonse.objects.get(id=id, hidden=False)
    except Annonse.DoesNotExist:
        return render(request, 'main/fjelltreffen/show_not_found.html')

    context = {}
    if request.method == 'POST':
        form = ReplyForm(request.POST) if request.user.is_authenticated() else ReplyAnonForm(request.POST)
        if form.is_valid():
            try:
                # Send the reply-email
                email_context = RequestContext(request, {
                    'annonse': annonse,
                    'reply': {
                        'name': request.POST['name'],
                        'email': request.POST['email'],
                        'text': request.POST['text']}
                    })
                content = render_to_string('main/fjelltreffen/reply_email.txt', email_context)
                send_mail('DNT Fjelltreffen - Svar fra %s' % request.POST['name'], content, request.POST['email'], [annonse.email], fail_silently=False)
                request.session['fjelltreffen.reply'] = {
                    'name': form.cleaned_data['name'],
                    'email': form.cleaned_data['email'],
                    'text': form.cleaned_data['text']
                }
                return HttpResponseRedirect(reverse('fjelltreffen.views.show_reply_sent', args=[annonse.id]))
            except Exception:
                # Use both a message (for consistency with the report-failure)
                # and context to be able to manipulate the template based on message info
                messages.error(request, 'email_reply_failure')
                context.update({'email_reply_failure': True})
                logger.error(u"Klarte ikke å sende Fjelltreffen-epost",
                    exc_info=sys.exc_info(),
                    extra={'request': request}
                )
    else:
        if request.user.is_authenticated():
            form = ReplyForm(initial={
                'name': request.user.get_profile().get_full_name(),
                'email': request.user.get_profile().get_email()
            })
        else:
            form = ReplyAnonForm()

    report = ''
    if 'fjelltreffen.report' in request.session:
        report = request.session['fjelltreffen.report']
        del request.session['fjelltreffen.report']

    context.update({
        'annonse': annonse,
        'form': form,
        'report': report})
    return render(request, 'main/fjelltreffen/show.html', context)

def show_reply_sent(request, id):
    if not 'fjelltreffen.reply' in request.session:
        return HttpResponseRedirect(reverse('fjelltreffen.views.show', args=[id]))
    annonse = Annonse.objects.get(id=id, hidden=False)
    context = {
        'annonse': annonse,
        'reply': request.session['fjelltreffen.reply']}
    del request.session['fjelltreffen.reply']
    return render(request, 'main/fjelltreffen/show_reply_sent.html', context)

@user_requires_login(message='fjelltreffen_login_required_for_report')
def report(request, id):
    if request.method == 'GET':
        # This route will be used when redirecting to login page with 'next' and the user logs in
        return HttpResponseRedirect(reverse('fjelltreffen.views.show', args=[id]))
    elif request.method == 'POST':
        try:
            annonse = Annonse.objects.get(id=id, hidden=False)
            request.session['fjelltreffen.report'] = {'reason': request.POST['reason']}

            context = RequestContext(request, {
                'annonse': annonse,
                'notifier': request.user.get_profile(),
                'reason': request.POST['reason']})
            content = render_to_string('main/fjelltreffen/report_email.txt', context)

            send_mail('Fjelltreffen - melding om upassende annonse', content, settings.DEFAULT_FROM_EMAIL, [settings.FJELLTREFFEN_REPORT_EMAIL], fail_silently=False)
            return HttpResponseRedirect(reverse('fjelltreffen.views.show_report_sent', args=[annonse.id]))
        except Exception:
            messages.error(request, 'email_report_failure')
            logger.error(u"Klarte ikke å sende Fjelltreffen rapporteringsepost",
                exc_info=sys.exc_info(),
                extra={'request': request}
            )
        return HttpResponseRedirect(reverse('fjelltreffen.views.show', args=[annonse.id]))

def show_report_sent(request, id):
    if not 'fjelltreffen.report' in request.session:
        return HttpResponseRedirect(reverse('fjelltreffen.views.show', args=[id]))
    annonse = Annonse.objects.get(id=id, hidden=False)
    context = {
        'annonse': annonse,
        'report': request.session['fjelltreffen.report']}
    del request.session['fjelltreffen.report']
    return render(request, 'main/fjelltreffen/show_report_sent.html', context)

#
# Actions for logged-in users (crud)
#

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.become_member')
@user_requires(lambda u: u.get_profile().get_actor().get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def new(request):
    if not request.user.get_profile().get_actor().get_balance().is_payed():
        return render(request, 'main/fjelltreffen/payment_required.html')

    other_active_annonse_exists = Annonse.objects.filter(profile=request.user.get_profile(), hidden=False).exists()
    context = {
        'counties': County.typical_objects().order_by('name'),
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS,
        'obscured_age': Annonse.obscure_age(request.user.get_profile().get_actor().get_age()),
        'other_active_annonse_exists': other_active_annonse_exists}
    return render(request, 'main/fjelltreffen/edit.html', context)

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.become_member')
@user_requires(lambda u: u.get_profile().get_actor().get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def edit(request, id):
    try:
        annonse = Annonse.objects.get(id=id)
        #checks if the user is the owner
        if annonse.profile != request.user.get_profile():
            raise PermissionDenied
    except Annonse.DoesNotExist:
        return render(request, 'main/fjelltreffen/edit_not_found.html')

    other_active_annonse_exists = Annonse.objects.exclude(id=annonse.id).filter(profile=request.user.get_profile(), hidden=False).exists()
    context = {
        'annonse': annonse,
        'counties': County.typical_objects().order_by('name'),
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS,
        'obscured_age': Annonse.obscure_age(request.user.get_profile().get_actor().get_age()),
        'other_active_annonse_exists': other_active_annonse_exists}
    return render(request, 'main/fjelltreffen/edit.html', context)

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.become_member')
@user_requires(lambda u: u.get_profile().get_actor().get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
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
        annonse = Annonse.objects.get(id=request.POST['id'])
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

    hidden = request.POST.get('hidden', '') == 'on'

    # Don't allow showing an already hidden annonse when you haven't payed
    if request.POST['id'] != '':
        if annonse.hidden and not request.user.get_profile().get_actor().get_balance().is_payed():
            hidden = True

    # Don't create new annonser if you already have an active annonse
    if request.POST['id'] == '':
        annonser_to_check = Annonse.get_active()
    else:
        annonser_to_check = Annonse.get_active().exclude(id=request.POST['id'])
    if annonser_to_check.filter(profile=request.user.get_profile()).exists():
        hidden = True

    annonse.county = County.objects.get(code=request.POST['county'])
    annonse.email = request.POST['email']
    annonse.title = request.POST['title']
    annonse.image = request.POST.get('image', '')
    annonse.text = request.POST['text']
    annonse.hidden = hidden
    annonse.hideage = request.POST['hideage'] == 'hide'
    annonse.save()
    return HttpResponseRedirect(reverse('fjelltreffen.views.mine'))

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.become_member')
@user_requires(lambda u: u.get_profile().get_actor().get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def delete(request, id):
    try:
        annonse = Annonse.objects.get(id=id)
        if annonse.profile != request.user.get_profile():
            #someone is trying to delete an annonse that dosent belong to them
            raise PermissionDenied
        else:
            annonse.delete()
            return HttpResponseRedirect(reverse('fjelltreffen.views.mine'))
    except Annonse.DoesNotExist:
        # Ignore - maybe a double-request, or something. They can try again if something failed.
        return HttpResponseRedirect(reverse('fjelltreffen.views.mine'))

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.become_member')
@user_requires(lambda u: u.get_profile().get_actor().get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def mine(request):
    #all annonser that belongs to the current user
    mine = Annonse.objects.filter(profile=request.user.get_profile())
    active_period = date.today() - timedelta(days=settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS)
    annonser = {
        'active': mine.filter(date__gte=active_period, hidden=False).order_by('-date', 'title'),
        'hidden': mine.filter(date__gte=active_period, hidden=True).order_by('-date', 'title'),
        'expired': mine.filter(date__lt=active_period).order_by('-date', 'title')}

    context = {
        'annonser': annonser,
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS}
    return render(request, 'main/fjelltreffen/mine.html', context)

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.become_member')
@user_requires(lambda u: u.get_profile().get_actor().get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def show_mine(request, id):
    if not request.user.get_profile().get_actor().get_balance().is_payed():
        messages.error(request, 'membership_not_payed')
        return HttpResponseRedirect(reverse('fjelltreffen.views.mine'))

    # Hide all other annonser that belongs to this user first
    hidden = Annonse.get_active().filter(profile=request.user.get_profile()).update(hidden=True)
    if hidden > 0:
        messages.info(request, 'max_one_active_annonse')
    annonse = Annonse.objects.get(id=id, profile=request.user.get_profile())
    annonse.hidden = False
    annonse.save()
    return HttpResponseRedirect(reverse('fjelltreffen.views.mine'))

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.become_member')
@user_requires(lambda u: u.get_profile().get_actor().get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def hide_mine(request, id):
    annonse = Annonse.objects.get(id=id, profile=request.user.get_profile())
    annonse.hidden = True
    annonse.save()
    return HttpResponseRedirect(reverse('fjelltreffen.views.mine'))

#
# View for a user that doesn't pass the age test
#

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: u.get_profile().memberid is not None, redirect_to='user.views.become_member')
def too_young(request):
    context = {
        'age_limit': settings.FJELLTREFFEN_AGE_LIMIT,
        'remaining_years': settings.FJELLTREFFEN_AGE_LIMIT - request.user.get_profile().get_actor().get_age()}
    return render(request, 'main/fjelltreffen/too_young.html', context)
