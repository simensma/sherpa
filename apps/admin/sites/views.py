import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from core.models import Site
from foreninger.models import Forening
from page.models import Menu, Page, Variant, Version

logger = logging.getLogger('sherpa')

def index(request):
    # Generate a list of children-foreninger with site to display
    children_foreninger_with_site = []
    for forening in request.active_forening.get_children_deep():
        # Verify that the forening has at least one site
        if forening.sites.count() == 0:
            continue

        # Check that the user has admin-access to the forening
        # This would be mighty slow if user.all_foreninger wasn't cached
        for user_forening in request.user.all_foreninger():
            if forening == user_forening and user_forening.role == 'admin':
                children_foreninger_with_site.append(forening)

    context = {
        'children_foreninger_with_site': children_foreninger_with_site,
    }
    return render(request, 'common/admin/sites/index.html', context)

def show(request, site):
    active_site = Site.objects.get(id=site)

    context = {
        'active_site': active_site,
        'ga_profile_id': Site.GA_PROFILE_ID_MAPPING.get(active_site.analytics_ua),
        'ga_account_username': settings.GA_ACCOUNT_USERNAME,
        'ga_account_password': settings.GA_ACCOUNT_PASSWORD,
    }
    return render(request, 'common/admin/sites/show.html', context)

def create(request):
    if not request.user.is_admin_in_forening(request.active_forening):
        return render(request, 'common/admin/sites/create_disallowed.html')

    # We need to know client-side which of the users' available foreninger already has a homepage site, to be able
    # to hide that option when the chosen forening is changed. We'll do a lookup based on the users already cached
    # forening-list, but with sites prefetching here, and send the mapping to the client.
    user_forening_ids = [f.id for f in request.user.all_foreninger()]
    foreninger_with_sites = Forening.objects.filter(id__in=user_forening_ids).prefetch_related('sites')
    foreninger_with_homepage = json.dumps({
        f.id: f.get_homepage_site(prefetched=True) is not None
        for f in foreninger_with_sites
    })

    available_site_types = []
    for t in Site.TYPE_CHOICES:
        if t[0] == 'mal':
            if not request.user.has_perm('sherpa_admin'):
                continue
        available_site_types.append(t)

    site_templates = Site.objects.filter(
        forening=Forening.DNT_CENTRAL_ID,
        type='mal',
    ).order_by('title')

    context = {
        'available_site_types': available_site_types,
        'foreninger_with_homepage': foreninger_with_homepage,
        'site_templates': site_templates,
        'template_types': Site.TEMPLATE_TYPE_CHOICES,
    }

    if request.method == 'GET':
        return render(request, 'common/admin/sites/create.html', context)

    elif request.method == 'POST':
        if not request.POST.get('type', '') in [t[0] for t in Site.TYPE_CHOICES]:
            raise PermissionDenied

        if request.POST['type'] == 'mal' and not request.user.has_perm('sherpa_admin'):
            raise PermissionDenied

        if not request.POST['domain-type'] in ['fqdn', 'subdomain']:
            raise PermissionDenied

        site_forening = Forening.objects.get(id=request.POST['site_forening'])
        if site_forening not in request.user.all_foreninger():
            raise PermissionDenied

        domain = request.POST['domain'].strip().lower()
        subdomain = domain
        if request.POST['domain-type'] == 'subdomain':
            domain = '%s.test.turistforeningen.no' % domain
        domain = domain.replace('http://', '').rstrip('/')

        if request.POST['type'] == 'forening' and site_forening.get_homepage_site() is not None:
            messages.error(request, 'main_site_exists')
            if request.POST['domain-type'] == 'fqdn':
                context['domain'] = domain
            else:
                context['domain'] = subdomain
            return render(request, 'common/admin/sites/create.html', context)

        result = Site.verify_domain(domain)
        if not result['valid']:
            messages.error(request, result['error'])
            if request.POST['domain-type'] == 'fqdn':
                context['domain'] = domain
            else:
                context['domain'] = subdomain
            if result['error'] == 'site_exists':
                context['existing_forening'] = result['existing_forening']
                context['existing_domain'] = domain
            return render(request, 'common/admin/sites/create.html', context)
        else:
            site = Site(
                domain=result['domain'],
                prefix=result['prefix'],
                type=request.POST['type'],
                template='local',
                forening=site_forening,
                title='',
            )
            if request.POST['type'] in ['hytte', 'kampanje', 'mal']:
                site.title = request.POST['title'].strip()

            if request.POST['type'] == 'mal':
                template_type = request.POST.get('template_type', '').strip()
                if template_type not in [t[0] for t in Site.TEMPLATE_TYPE_CHOICES]:
                    raise PermissionDenied
                site.template_type = template_type
                site.template_description = request.POST.get('template_description', '').strip()
            else:
                site.template_type = ''
                site.template_description = ''

            site.save()

            # Invalidate the forening's homepage site cache
            cache.delete('forening.homepage_site.%s' % site_forening.id)

            page = Page(
                title='Forside',
                slug='',
                published=False,
                created_by=request.user,
                site=site,
            )
            page.save()

            variant = Variant(
                page=page,
                article=None,
                name='Standard',
                segment=None,
                priority=1,
                owner=request.user,
            )
            variant.save()

            version = Version(
                variant=variant,
                version=1,
                owner=request.user,
                active=True,
                ads=True,
            )
            version.save()

            menu = Menu(
                name='Forside',
                url='http://%s/' % site.domain,
                order=1,
                site=site,
            )
            menu.save()

            if 'use-template' in request.POST:
                # User explicitly requested not to clone any template
                pass
            elif request.POST.get('template', '').strip() == '':
                # Sherpa-admin error; a site-template for the chosen site type doesn't exist!
                # This needs to be fixed.
                logger.error(u"Sherpa-bruker opprettet en site med en mal som ikke finnes",
                    extra={
                        'request': request,
                        'missing_template_type': request.POST.get('missing-template-type', '<unknown>'),
                    }
                )
            else:
                # Template-site TODO
                pass

            request.session.modified = True
            return redirect('admin.sites.views.created', site.id)

def created(request, site):
    if not request.user.is_admin_in_forening(request.active_forening):
        raise PermissionDenied

    site = Site.objects.get(id=site)
    forside_version = Version.objects.get(
        variant__page__title='Forside',
        variant__page__site=site,
    )
    context = {
        'created_site': site,
        'forside_version': forside_version,
    }
    return render(request, 'common/admin/sites/created.html', context)
