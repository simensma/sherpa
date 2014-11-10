from django.shortcuts import render, redirect
from django.contrib import messages

from core.models import Site

def index(request, site):
    active_site = Site.objects.get(id=site)
    context = {'active_site': active_site}
    if 'message_context' in request.session:
        context['message_context'] = request.session['message_context']
        del request.session['message_context']
    return render(request, 'common/admin/sites/settings/index.html', context)

def save(request, site):
    if request.method != 'POST':
        return redirect('admin.sites.settings.views.index', site)

    active_site = Site.objects.get(id=site)
    domain = request.POST['domain'].strip().lower().replace('http://', '').rstrip('/')

    if domain == active_site.domain:
        # Special case; the domain wasn't changed - so just say that it worked
        messages.info(request, 'domain_updated')
    else:
        result = Site.verify_domain(domain)
        if not result['valid']:
            messages.error(request, result['error'])
            if result['error'] == 'site_exists':
                request.session['message_context'] = {'existing_forening': result['existing_forening']}
        else:
            messages.info(request, 'domain_updated')
            active_site.domain = result['domain']
            active_site.prefix = result['prefix']

    active_site.is_published = 'published' in request.POST
    active_site.save()

    request.session.modified = True
    return redirect('admin.sites.settings.views.index', active_site.id)
