import json

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from core.models import Site
from foreninger.models import Forening

def index(request, site):
    active_site = Site.objects.get(id=site)

    # We need to know client-side which of the users' available foreninger already has a homepage site, to be able
    # to hide that option when the chosen forening is changed. We'll do a lookup based on the users already cached
    # forening-list, but with sites prefetching here, and send the mapping to the client.
    user_forening_ids = [f.id for f in request.user.all_foreninger()]
    foreninger_with_sites = Forening.objects.filter(id__in=user_forening_ids).prefetch_related('sites')
    foreninger_with_other_homepage = json.dumps({
        f.id: f.get_homepage_site(prefetched=True) is not None and f.get_homepage_site(prefetched=True) != active_site
        for f in foreninger_with_sites
    })

    available_site_types = []
    for t in Site.TYPE_CHOICES:
        if t[0] == 'mal':
            if not request.user.has_perm('sherpa_admin'):
                continue
        available_site_types.append(t)

    context = {
        'active_site': active_site,
        'available_site_types': available_site_types,
        'foreninger_with_other_homepage': foreninger_with_other_homepage,
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
    domain = request.POST['domain'].strip().lower().replace('http://', '').rstrip('/')
    errors = False

    site_forening = Forening.objects.get(id=request.POST['site_forening'])
    if site_forening not in request.user.all_foreninger():
        raise PermissionDenied

    type = request.POST['type']
    if type not in [t[0] for t in Site.TYPE_CHOICES]:
        raise PermissionDenied

    homepage = site_forening.get_homepage_site()
    if type == 'forening' and homepage is not None and homepage != active_site:
        # The chosen forening has *another* homepage site
        messages.error(request, 'homepage_site_exists')
        return redirect('admin.sites.settings.views.index', site)

    if type == 'mal' and not request.user.has_perm('sherpa_admin'):
        raise PermissionDenied

    active_site.forening = site_forening
    active_site.type = type

    if type in ['hytte', 'kampanje', 'mal']:
        active_site.title = request.POST['title'].strip()
    else:
        active_site.title = ''

    if type == 'mal':
        template_type = request.POST.get('template_type', '').strip()
        if template_type not in [t[0] for t in Site.TEMPLATE_TYPE_CHOICES]:
            raise PermissionDenied
        active_site.template_type = template_type
        active_site.template_description = request.POST.get('template_description', '').strip()
    else:
        active_site.template_type = ''
        active_site.template_description = ''

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

    request.session.modified = True
    if not errors:
        messages.info(request, 'settings_saved')
    return redirect('admin.sites.settings.views.index', active_site.id)
