from __future__ import absolute_import

import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from .forms import SiteForm
from admin.models import Campaign
from articles.models import Article
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

    # Verify that all template-sites exists
    missing_templates = []
    if request.user.has_perm('sherpa_admin'):
        for type in Site.TEMPLATE_TYPE_CHOICES:
            if not Site.objects.filter(type='mal', template_main=True, template_type=type[0]).exists():
                missing_templates.append(type)

    context = {
        'children_foreninger_with_site': children_foreninger_with_site,
        'missing_templates': missing_templates,
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
        context['form'] = SiteForm(request.user, auto_id='%s')
        return render(request, 'common/admin/sites/create.html', context)

    elif request.method == 'POST':
        form = SiteForm(request.user, request.POST, auto_id='%s')
        context['form'] = form

        if not form.is_valid():
            return render(request, 'common/admin/sites/create.html', context)

        if not request.POST['domain-type'] in ['fqdn', 'subdomain']:
            raise PermissionDenied

        site_forening = form.cleaned_data['forening']
        type = form.cleaned_data['type']
        title = form.cleaned_data['title']

        domain = request.POST['domain'].strip().lower()
        subdomain = domain
        if request.POST['domain-type'] == 'subdomain':
            domain = '%s.test.turistforeningen.no' % domain
        domain = domain.replace('http://', '').rstrip('/')

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
                type=type,
                template='local',
                forening=site_forening,
                title=title,
            )

            if type == 'mal':
                template_type = request.POST.get('template_type', '').strip()
                if template_type not in [t[0] for t in Site.TEMPLATE_TYPE_CHOICES]:
                    raise PermissionDenied
                site.template_main = 'template_main' in request.POST
                site.template_type = template_type
                site.template_description = request.POST.get('template_description', '').strip()
            else:
                site.template_main = False
                site.template_type = ''
                site.template_description = ''

            site.save()

            # If this is a main template, clear other templates of this type in case any of them were previous main
            if site.type == 'mal' and site.template_main:
                Site.objects.filter(
                    type=site.type,
                    template_type=site.template_type,
                ).exclude(
                    id=site.id,
                ).update(
                    template_main=False
                )

            # Invalidate the forening's homepage site cache
            cache.delete('forening.homepage_site.%s' % site_forening.id)

            if 'use-template' not in request.POST:
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
                # All right, let's clone the entire template site
                # Note that for most objects, we'll just set the primary key to None, change the site field to the
                # new site, and save it, which will insert a new object.
                # For related fields, we'll need to save the related set in memory before saving the new object, so
                # that we can iterate it, clone them and re-relate them to the new object
                template_site = Site.objects.get(id=request.POST['template'], type='mal')

                # Menus
                for menu in Menu.objects.filter(site=template_site):
                    menu.id = None
                    menu.site = site
                    menu.save()

                # Pages
                for page in Page.objects.filter(site=template_site):
                    variants = page.variant_set.all()
                    page.id = None
                    page.site = site

                    # Change creation to the user creating the new site and reset modification
                    page.created_by = request.user
                    page.created_date = datetime.now()
                    page.modified_by = None
                    page.modified_date = None

                    page.save()

                    for variant in variants:
                        versions = variant.version_set.all()
                        variant.id = None
                        variant.page = page
                        variant.save()

                        for version in versions:
                            rows = version.rows.all()
                            version.id = None
                            version.variant = variant
                            version.save()

                            for row in rows:
                                columns = row.columns.all()
                                row.id = None
                                row.version = version
                                row.save()

                                for column in columns:
                                    contents = column.contents.all()
                                    column.id = None
                                    column.row = row
                                    column.save()

                                    for content in contents:
                                        content.id = None
                                        content.column = column
                                        content.save()

                # Articles
                for article in Article.objects.filter(site=template_site):
                    variants = article.variant_set.all()
                    article.id = None
                    article.site = site

                    # Change creation to the user creating the new site and reset modification
                    article.created_by = request.user
                    article.created_date = datetime.now()
                    article.modified_by = None
                    article.modified_date = None

                    article.save()

                    for variant in variants:
                        versions = variant.version_set.all()
                        variant.id = None
                        variant.article = article
                        variant.save()

                        for version in versions:
                            rows = version.rows.all()
                            version.id = None
                            version.variant = variant
                            version.save()

                            for row in rows:
                                columns = row.columns.all()
                                row.id = None
                                row.version = version
                                row.save()

                                for column in columns:
                                    contents = column.contents.all()
                                    column.id = None
                                    column.row = row
                                    column.save()

                                    for content in contents:
                                        content.id = None
                                        content.column = column
                                        content.save()

                # Campaigns
                for campaign in Campaign.objects.filter(site=template_site):
                    campaign_texts = campaign.text.all()
                    campaign.id = None
                    campaign.site = site
                    campaign.save()

                    for campaign_text in campaign_texts:
                        campaign_text.id = None
                        campaign_text.campaign = campaign
                        campaign_text.save()

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
