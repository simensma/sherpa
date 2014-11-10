from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from core.models import Site

def index(request, site):
    active_site = Site.objects.get(id=site)
    context = {
        'active_site': active_site,
        'site_types': Site.TYPE_CHOICES,
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

    type = request.POST['type']
    if type not in [t[0] for t in Site.TYPE_CHOICES]:
        raise PermissionDenied

    active_site.type = type

    if type in ['hytte', 'kampanje']:
        active_site.title = request.POST['title'].strip()
    else:
        active_site.title = ''

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
