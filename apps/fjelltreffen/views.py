# encoding: utf-8
from datetime import date, timedelta
import json
import sys
import logging
from cStringIO import StringIO
import hashlib

from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import PermissionDenied

import PIL.Image
import boto

from admin.images.util import standardize_extension
from sherpa.decorators import user_requires, user_requires_login
from fjelltreffen.models import Annonse
from fjelltreffen.forms import ReplyForm, ReplyAnonForm
from fjelltreffen.util import parse_for_spam
from core import validator, librato
from core.models import County
from core.util import s3_bucket

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
        'filter': request.session.get('fjelltreffen.filter')
    }
    return render(request, 'central/fjelltreffen/index.html', context)

def load(request):
    if not request.is_ajax() or request.method != 'POST' or not 'filter' in request.POST:
        raise PermissionDenied

    filter = json.loads(request.POST['filter'])
    start_index = request.POST['start_index']

    request.session['fjelltreffen.filter'] = {
        'minage': filter['minage'],
        'maxage': filter['maxage'],
        'gender': filter['gender'], # Empty gender means both genders
        'county': filter['county'],
        'text': filter['text']
    }

    annonser, start_index, end = Annonse.get_by_filter(request.session['fjelltreffen.filter'], int(start_index))

    context = RequestContext(request)
    context['annonser'] = annonser
    string = render_to_string('central/fjelltreffen/annonselist.html', context)
    return HttpResponse(json.dumps({
        'html': string,
        'start_index': start_index,
        'end': end}))

def show(request, id):
    try:
        annonse = Annonse.objects.get(id=id, hidden=False)
    except Annonse.DoesNotExist:
        return render(request, 'central/fjelltreffen/show_not_found.html')

    context = {}
    if request.method == 'POST':
        form = ReplyForm(request.POST) if request.user.is_authenticated() else ReplyAnonForm(request.POST)
        if form.is_valid():
            try:
                # Send the reply-email
                email_context = RequestContext(request, {
                    'annonse': annonse,
                    'reply': {
                        'name': form.cleaned_data['name'],
                        'email': form.cleaned_data['email'],
                        'text': form.cleaned_data['text']
                    }
                })
                content = render_to_string('central/fjelltreffen/reply_email.txt', email_context)
                parse_for_spam(request, form.cleaned_data['name'], form.cleaned_data['email'], form.cleaned_data['text'], annonse)
                send_mail('DNT Fjelltreffen - Svar fra %s' % form.cleaned_data['name'], content, settings.DEFAULT_FROM_EMAIL, [annonse.email], fail_silently=False)
                librato.increment('sherpa.fjelltreffen_svar')
                request.session['fjelltreffen.reply'] = {
                    'name': form.cleaned_data['name'],
                    'email': form.cleaned_data['email'],
                    'text': form.cleaned_data['text']
                }
                return redirect('fjelltreffen.views.show_reply_sent', annonse.id)
            except Exception:
                # Use both a message (for consistency with the report-failure)
                # and context to be able to manipulate the template based on message info
                messages.error(request, 'email_reply_failure')
                context.update({'email_reply_failure': True})
                logger.warning(u"Klarte ikke å sende Fjelltreffen-epost",
                    exc_info=sys.exc_info(),
                    extra={'request': request}
                )
    else:
        if request.user.is_authenticated():
            form = ReplyForm(initial={
                'name': request.user.get_full_name(),
                'email': request.user.get_email()
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
    return render(request, 'central/fjelltreffen/show.html', context)

def show_reply_sent(request, id):
    if not 'fjelltreffen.reply' in request.session:
        return redirect('fjelltreffen.views.show', id)
    annonse = Annonse.objects.get(id=id, hidden=False)
    context = {
        'annonse': annonse,
        'reply': request.session['fjelltreffen.reply']
    }
    del request.session['fjelltreffen.reply']
    return render(request, 'central/fjelltreffen/show_reply_sent.html', context)

@user_requires_login(message='fjelltreffen_login_required_for_report')
def report(request, id):
    if request.method == 'GET':
        # This route will be used when redirecting to login page with 'next' and the user logs in
        return redirect('fjelltreffen.views.show', id)
    elif request.method == 'POST':
        try:
            annonse = Annonse.objects.get(id=id, hidden=False)
            request.session['fjelltreffen.report'] = {'reason': request.POST['reason']}

            context = RequestContext(request, {
                'annonse': annonse,
                'notifier': request.user,
                'reason': request.POST['reason']})
            content = render_to_string('central/fjelltreffen/report_email.txt', context)

            send_mail('Fjelltreffen - melding om upassende annonse', content, settings.DEFAULT_FROM_EMAIL, [settings.FJELLTREFFEN_REPORT_EMAIL], fail_silently=False)
            return redirect('fjelltreffen.views.show_report_sent', annonse.id)
        except Exception:
            messages.error(request, 'email_report_failure')
            logger.error(u"Klarte ikke å sende Fjelltreffen rapporteringsepost",
                exc_info=sys.exc_info(),
                extra={'request': request}
            )
        return redirect('fjelltreffen.views.show', annonse.id)

def show_report_sent(request, id):
    if not 'fjelltreffen.report' in request.session:
        return redirect('fjelltreffen.views.show', id)
    annonse = Annonse.objects.get(id=id, hidden=False)
    context = {
        'annonse': annonse,
        'report': request.session['fjelltreffen.report']
    }
    del request.session['fjelltreffen.report']
    return render(request, 'central/fjelltreffen/show_report_sent.html', context)

def about(request):
    return render(request, 'central/fjelltreffen/about.html')

#
# Actions for logged-in users (crud)
#

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def new(request):
    if not request.user.has_paid():
        return render(request, 'central/fjelltreffen/payment_required.html')

    other_active_annonse_exists = Annonse.get_active().filter(user=request.user, hidden=False).exists()
    context = {
        'counties': County.typical_objects().order_by('name'),
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS,
        'obscured_age': Annonse.obscure_age(request.user.get_age()),
        'other_active_annonse_exists': other_active_annonse_exists
    }
    return render(request, 'central/fjelltreffen/edit.html', context)

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def edit(request, id):
    try:
        annonse = Annonse.objects.get(id=id)
        #checks if the user is the owner
        if annonse.user != request.user:
            raise PermissionDenied
    except Annonse.DoesNotExist:
        return render(request, 'central/fjelltreffen/edit_not_found.html')

    other_active_annonse_exists = Annonse.get_active().exclude(id=annonse.id).filter(user=request.user).exists()
    context = {
        'annonse': annonse,
        'counties': County.typical_objects().order_by('name'),
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS,
        'obscured_age': Annonse.obscure_age(request.user.get_age()),
        'other_active_annonse_exists': other_active_annonse_exists
    }
    return render(request, 'central/fjelltreffen/edit.html', context)

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def save(request):
    if request.method != 'POST':
        return redirect('fjelltreffen.views.mine')

    # If user hasn't paid, allow editing, but not creating new annonser
    if not request.user.has_paid() and request.POST['id'] == '':
        raise PermissionDenied

    # Pre-save validations
    errors = False

    if request.POST.get('id', '') == '':
        # New annonse (not editing an existing one), create it
        annonse = Annonse()
        annonse.user = request.user
    else:
        annonse = Annonse.objects.get(id=request.POST['id'])
        if annonse.user != request.user:
            #someone is trying to edit an annonse that dosent belong to them
            raise PermissionDenied

    if request.POST.get('title', '') == '':
        messages.error(request, 'missing_title')
        errors = True

    if not validator.email(request.POST['email']):
        messages.error(request, 'invalid_email')
        errors = True

    if request.POST.get('text', '') == '':
        messages.error(request, 'missing_text')
        errors = True

    if 'image' in request.FILES:
        try:
            # Uploading image
            file = request.FILES['image']
            data = file.read()
            extension = standardize_extension(file.name.split(".")[-1])

            # Create the thumbnail
            thumb = PIL.Image.open(StringIO(data)).copy()
            fp = StringIO()
            thumb.thumbnail([settings.FJELLTREFFEN_IMAGE_THUMB_SIZE, settings.FJELLTREFFEN_IMAGE_THUMB_SIZE], PIL.Image.ANTIALIAS)
            thumb.save(fp, extension)
            thumb_data = fp.getvalue()

            # Calculate sha1-hashes
            sha1 = hashlib.sha1()
            sha1.update(data)
            hash = sha1.hexdigest()
            sha1 = hashlib.sha1()
            sha1.update(thumb_data)
            thumb_hash = sha1.hexdigest()
        except Exception:
            logger.error(u"Kunne ikke laste opp Fjelltreffen-bilde",
                exc_info=sys.exc_info(),
                extra={'request': request}
            )
            messages.error(request, 'image_upload_error')
            errors = True

    if errors:
        if request.POST.get('id', '') == '':
            return redirect('fjelltreffen.views.new')
        else:
            return redirect('fjelltreffen.views.edit', request.POST['id'])

    hidden = request.POST.get('hidden', 'hide') == 'hide'

    # Don't allow showing an already hidden annonse when you haven't paid
    if request.POST['id'] != '':
        if annonse.hidden and not request.user.has_paid():
            hidden = True

    # Don't create new annonser if you already have an active annonse
    if request.POST.get('id', '') == '':
        annonser_to_check = Annonse.get_active()
    else:
        annonser_to_check = Annonse.get_active().exclude(id=request.POST['id'])
    if annonser_to_check.filter(user=request.user).exists():
        hidden = True

    if request.POST.get('county', '') == 'international':
        annonse.county = None
    else:
        annonse.county = County.objects.get(id=request.POST.get('county', ''))
    # TODO: Validate and return form to user with error message
    annonse.title = request.POST.get('title', '')[:255]
    annonse.email = request.POST.get('email', '')[:255]
    if 'image' in request.FILES:
        # Delete any existing image
        annonse.delete_image()

        # Setup AWS connection
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(s3_bucket())

        # Upload the original image to AWS
        key = bucket.new_key("%s/%s.%s" % (settings.AWS_FJELLTREFFEN_IMAGES_PREFIX, hash, extension))
        key.content_type = file.content_type.encode('utf-8') # Give boto an encoded str, not unicode
        key.set_contents_from_string(data, policy='public-read')

        # Upload the thumbnail to AWS
        key = bucket.new_key("%s/%s.%s" % (settings.AWS_FJELLTREFFEN_IMAGES_PREFIX, thumb_hash, extension))
        key.content_type = file.content_type.encode('utf-8') # Give boto an encoded str, not unicode
        key.set_contents_from_string(thumb_data, policy='public-read')

        # Update the DB fields with new images
        annonse.image = "%s.%s" % (hash, extension)
        annonse.image_thumb = "%s.%s" % (thumb_hash, extension)

        # In case this was an annonse with imported image, specify that it itsn't anymore
        annonse.is_image_old = False
    annonse.text = request.POST.get('text', '')
    annonse.hidden = hidden
    annonse.hideage = request.POST.get('hideage', '') == 'hide'
    annonse.save()
    return redirect('fjelltreffen.views.mine')

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def delete(request, id):
    try:
        annonse = Annonse.objects.get(id=id)
        if annonse.user != request.user:
            #someone is trying to delete an annonse that dosent belong to them
            raise PermissionDenied
        else:
            annonse.delete()
            return redirect('fjelltreffen.views.mine')
    except Annonse.DoesNotExist:
        # Ignore - maybe a double-request, or something. They can try again if something failed.
        return redirect('fjelltreffen.views.mine')

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def mine(request):
    #all annonser that belongs to the current user
    mine = Annonse.objects.filter(user=request.user)
    active_period = date.today() - timedelta(days=settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS)

    active = mine.filter(date_renewed__gte=active_period, hidden=False).order_by('-date_added', 'title')
    hidden = mine.filter(date_renewed__gte=active_period, hidden=True).order_by('-date_added', 'title')
    expired = mine.filter(date_renewed__lt=active_period).order_by('-date_added', 'title')

    annonser = list(active) + list(hidden) + list(expired)

    context = {
        'annonser': annonser,
        'annonse_retention_days': settings.FJELLTREFFEN_ANNONSE_RETENTION_DAYS
    }
    return render(request, 'central/fjelltreffen/mine.html', context)

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def show_mine(request, id):
    if not request.user.has_paid():
        messages.error(request, 'membership_not_paid')
        return redirect('fjelltreffen.views.mine')

    try:
        # Hide all other annonser that belongs to this user first
        hidden = Annonse.get_active().filter(user=request.user).update(hidden=True)
        if hidden > 0:
            messages.info(request, 'max_one_active_annonse')
        annonse = Annonse.objects.get(id=id, user=request.user)
        annonse.hidden = False
        annonse.save()
        return redirect('fjelltreffen.views.mine')
    except Annonse.DoesNotExist:
        # Unexpected case; maybe some asynchronous browsing. Ignore and return to the annonse-list
        return redirect('fjelltreffen.views.mine')

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def hide_mine(request, id):
    try:
        annonse = Annonse.objects.get(id=id, user=request.user)
        annonse.hidden = True
        annonse.save()
        return redirect('fjelltreffen.views.mine')
    except Annonse.DoesNotExist:
        # Unexpected case; maybe some asynchronous browsing. Ignore and return to the annonse-list
        return redirect('fjelltreffen.views.mine')

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def renew_mine(request, id):
    try:
        annonse = Annonse.objects.get(id=id, user=request.user)
        annonse.date_renewed = date.today()
        annonse.save()
        return redirect('fjelltreffen.views.mine')
    except Annonse.DoesNotExist:
        # Unexpected case; maybe some asynchronous browsing. Ignore and return to the annonse-list
        return redirect('fjelltreffen.views.mine')

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: not u.is_pending, redirect_to='user.views.home')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
@user_requires(lambda u: u.get_age() > settings.FJELLTREFFEN_AGE_LIMIT, redirect_to='fjelltreffen.views.too_young')
def delete_image(request, id):
    annonse = Annonse.objects.get(id=id, user=request.user)
    annonse.delete_image()
    return HttpResponse()

#
# View for a user that doesn't pass the age test
#

@user_requires_login(message='fjelltreffen_login_required')
@user_requires(lambda u: u.is_member(), redirect_to='user.views.register_membership')
def too_young(request):
    context = {
        'age_limit': settings.FJELLTREFFEN_AGE_LIMIT,
        'remaining_years': settings.FJELLTREFFEN_AGE_LIMIT - request.user.get_age()
    }
    return render(request, 'central/fjelltreffen/too_young.html', context)
