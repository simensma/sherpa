from __future__ import absolute_import

from datetime import datetime
import logging
import json
import re

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect

from .forms import CreateSiteForm
from admin.models import Campaign
from articles.models import Article
from core.models import Site
from foreninger.models import Forening
from page.models import Menu, Page

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
        'site_templates': site_templates,
        'template_types': Site.TEMPLATE_TYPE_CHOICES,
    }

    if request.method == 'GET':
        context['form'] = CreateSiteForm(request.user, auto_id='%s')
        return render(request, 'common/admin/sites/create.html', context)

    elif request.method == 'POST':
        form = CreateSiteForm(request.user, request.POST, auto_id='%s')
        context['form'] = form

        if not form.is_valid():
            return render(request, 'common/admin/sites/create.html', context)

        if not request.POST['domain-type'] in ['fqdn', 'subdomain']:
            raise PermissionDenied

        site_forening = form.cleaned_data['forening']
        type = form.cleaned_data['type']
        title = form.cleaned_data['title']
        template_main = form.cleaned_data['template_main']
        template_type = form.cleaned_data['template_type']
        template_description = form.cleaned_data['template_description']
        domain, prefix = form.cleaned_data['domain']

        site = Site(
            domain=domain,
            prefix=prefix,
            type=type,
            template='local',
            forening=site_forening,
            title=title,
            template_main=template_main,
            template_type=template_type,
            template_description=template_description,
        )

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
            # Additionally, replace domain name references in content from the template-domain to the new one
            template_site = Site.objects.get(id=request.POST['template'], type='mal')

            # Menus
            for menu in Menu.objects.filter(site=template_site):
                menu.id = None
                menu.site = site

                # Replace domain references with the new site domain
                menu.url = re.sub(template_site.domain, site.domain, menu.url)

                menu.save()

            # Pages
            for page in Page.objects.filter(site=template_site):
                variants = page.variant_set.all()
                page.id = None
                page.site = site

                # Reset MPTT state and let the mptt-manager recreate a new root node
                page.tree_id = None
                page.parent = None
                page.lft = None
                page.rght = None
                page.level = None

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

                                    # Replace domain references with the new site domain
                                    # Use a json dump with prepended/trailing quotes stripped to ensure the
                                    # replacement string is properly escaped if inserted into json-formatted content
                                    json_safe_domain = json.dumps(site.domain)[1:-1]
                                    content.content = re.sub(template_site.domain, json_safe_domain, content.content)

                                    # For aktiviteteslisting-widgets, force arranger-filter to the new site's related
                                    # forening
                                    if content.type == 'widget':
                                        parsed_content = json.loads(content.content)
                                        if parsed_content['widget'] == 'aktivitet_listing':
                                            # Note that the list of ids contains strings, because we forgot to convert
                                            # it to int in the widget-editor save logic, but that's not a problem since
                                            # the filter lookup will implicitly convert it. So force it to str to be
                                            # consistent
                                            parsed_content['foreninger'] = [str(site.forening.id)]
                                            content.content = json.dumps(parsed_content)

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

                                    # Replace domain references with the new site domain
                                    # Use a json dump with prepended/trailing quotes stripped to ensure the
                                    # replacement string is properly escaped if inserted into json-formatted content
                                    json_safe_domain = json.dumps(site.domain)[1:-1]
                                    content.content = re.sub(template_site.domain, json_safe_domain, content.content)

                                    # For aktiviteteslisting-widgets, force arranger-filter to the new site's related
                                    # forening
                                    if content.type == 'widget':
                                        parsed_content = json.loads(content.content)
                                        if parsed_content['widget'] == 'aktivitet_listing':
                                            # Note that the list of ids contains strings, because we forgot to convert
                                            # it to int in the widget-editor save logic, but that's not a problem since
                                            # the filter lookup will implicitly convert it. So force it to str to be
                                            # consistent
                                            parsed_content['foreninger'] = [str(site.forening.id)]
                                            content.content = json.dumps(parsed_content)

                                    content.save()

            # Campaigns
            for campaign in Campaign.objects.filter(site=template_site):
                campaign_texts = campaign.text.all()
                campaign.id = None
                campaign.site = site

                # Replace domain references with the new site domain
                campaign.button_anchor = re.sub(template_site.domain, site.domain, campaign.button_anchor)

                campaign.save()

                for campaign_text in campaign_texts:
                    campaign_text.id = None
                    campaign_text.campaign = campaign
                    campaign_text.save()

        request.session.modified = True
        messages.info(request, 'site_created')
        return redirect('admin.sites.views.show', site.id)
