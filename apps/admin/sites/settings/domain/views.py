from django.shortcuts import render, redirect
from django.contrib import messages

from core.models import Site

def index(request, site):
    active_site = Site.objects.get(id=site)
    context = {'active_site': active_site}

    if request.method == 'GET':
        return render(request, 'common/admin/sites/settings/domain/index.html', context)

    elif request.method == 'POST':
        domain = request.POST['domain'].strip().lower()

        if domain.replace('http://', '').rstrip('/') == active_site.domain:
            # Special case; the domain wasn't changed - so just say that it worked
            messages.info(request, 'domain_updated')
            return redirect('admin.sites.settings.domain.views.index', active_site.id)

        result = Site.verify_domain(domain)
        if not result['valid']:
            messages.error(request, result['error'])
            context['domain'] = domain
            if result['error'] == 'site_exists':
                context['existing_forening'] = result['existing_forening']
            return render(request, 'common/admin/sites/settings/domain/index.html', context)
        else:
            messages.info(request, 'domain_updated')
            active_site.domain = result['domain']
            active_site.prefix = result['prefix']
            active_site.save()
            request.session.modified = True
            return redirect('admin.sites.settings.domain.views.index', active_site.id)
