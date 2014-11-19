from django.contrib import messages
from django.shortcuts import render, redirect

from admin.sites.forms import SiteForm
from core.models import Site

def index(request, site):
    active_site = Site.objects.get(id=site)

    available_site_types = []
    for t in Site.TYPE_CHOICES:
        if t[0] == 'mal':
            if not request.user.has_perm('sherpa_admin'):
                continue
        available_site_types.append(t)

    if 'form_data' in request.session:
        form = request.session['form_data']
        del request.session['form_data']
    else:
        form = SiteForm(request.user, auto_id='%s')

    context = {
        'form': form,
        'active_site': active_site,
        'available_site_types': available_site_types,
        'template_types': Site.TEMPLATE_TYPE_CHOICES,
    }

    if 'message_context' in request.session:
        context['message_context'] = request.session['message_context']
        del request.session['message_context']

    return render(request, 'common/admin/sites/settings/index.html', context)

def save(request, site):
    if request.method != 'POST':
        return redirect('admin.sites.settings.views.index', site)

    active_site = Site.objects.get(id=site)
    form = SiteForm(request.user, request.POST, auto_id='%s')

    if not form.is_valid():
        request.session['form_data'] = form
        return redirect('admin.sites.settings.views.index', site)

    site_forening = form.cleaned_data['forening']
    type = form.cleaned_data['type']
    title = form.cleaned_data['title']
    template_main = form.cleaned_data['template_main']
    template_type = form.cleaned_data['template_type']
    template_description = form.cleaned_data['template_description']

    domain = request.POST['domain'].strip().lower().replace('http://', '').rstrip('/')
    errors = False

    active_site.forening = site_forening
    active_site.type = type
    active_site.title = title
    active_site.template_main = template_main
    active_site.template_type = template_type
    active_site.template_description = template_description

    if domain == active_site.domain:
        # Special case; the domain wasn't changed - so just pretend that it's updated
        pass
    else:
        result = Site.verify_domain(domain)
        if not result['valid']:
            messages.error(request, result['error'])
            errors = True
            if result['error'] == 'site_exists':
                request.session['message_context'] = {'existing_forening': result['existing_forening']}
        else:
            active_site.domain = result['domain']
            active_site.prefix = result['prefix']

    active_site.is_published = 'published' in request.POST
    active_site.save()

    # If this is a main template, clear other templates of this type in case any of them were previous main
    if active_site.type == 'mal' and active_site.template_main:
        Site.objects.filter(
            type=active_site.type,
            template_type=active_site.template_type,
        ).exclude(
            id=active_site.id,
        ).update(
            template_main=False
        )

    request.session.modified = True
    if not errors:
        messages.info(request, 'settings_saved')
    return redirect('admin.sites.settings.views.index', active_site.id)
