from django.shortcuts import render, redirect
from django.core.cache import cache
from django.db.models import Q
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from datetime import datetime, date
from lxml import etree
import requests
import re

# This ugly import hack imports the model from views because of namespace collision,
# should be 'from aktiviteter.models import Aktivitet'
from aktiviteter.views import Aktivitet
from focus.models import Actor
from page.models import Page, Variant, Version
from user.models import User
from core.models import Site
from admin.sites.pages.util import create_template

def index(request):
    total_membership_count = cache.get('admin.total_membership_count')
    local_membership_count = cache.get('admin.local_membership_count.%s' % request.active_forening.id)
    if total_membership_count is None or local_membership_count is None:
        all_active_members = Actor.all_active_members()
        total_membership_count = all_active_members.count()
        local_membership_count = all_active_members.filter(
            main_forening_id__in=[f.focus_id for f in request.active_forening.get_main_forenings()],
        ).count()
        cache.set('admin.total_membership_count', total_membership_count, 60 * 60 * 12)
        cache.set('admin.local_membership_count.%s' % request.active_forening.id, local_membership_count, 60 * 60 * 12)

    turledere = User.get_users().filter(turledere__isnull=False).distinct().count()
    if request.active_forening.get_homepage_site() is not None:
        pages = Page.on(request.active_forening.get_homepage_site()).filter(
            pub_date__lte=datetime.now(),
            published=True
        ).count()
    else:
        pages = None
    aktiviteter = Aktivitet.objects.filter(
        Q(forening=request.active_forening) |
        Q(co_forening=request.active_forening),
        pub_date__lte=date.today(),
        published=True,
        private=False,
    ).count()
    dashboard_stats = {
        'members': {
            'total': "{:,}".format(total_membership_count),
            'local': "{:,}".format(local_membership_count),
        },
        'turledere': turledere,
        'pages': pages,
        'aktiviteter': aktiviteter,
    }

    betablog = cache.get('admin.betablog')
    if betablog is None:
        try:
            betablog = []
            r = requests.get("http://beta.turistforeningen.no/", params={'feed': 'rss2'})
            channel = etree.fromstring(r.content).find('channel')
            for item in channel.findall('item'):
                content = item.find('description').text
                image = None
                m = re.search('<img.*?src="(.*?)" ', content)
                if m is not None:
                    image = m.group(1)
                pub_date = datetime.strptime(item.find('pubDate').text[:-6], "%a, %d %b %Y %H:%M:%S")

                betablog.append({
                    'title': item.find('title').text,
                    'link': item.find('link').text,
                    'content': content,
                    'image': image,
                    'pub_date': pub_date,
                })
        except requests.ConnectionError:
            pass

        cache.set('admin.betablog', betablog, 60 * 60 * 12)

    context = {
        'betablog': betablog,
        'dashboard_stats': dashboard_stats,
    }
    return render(request, 'common/admin/dashboard.html', context)

def setup_site(request):
    context = {'site_types': Site.TYPE_CHOICES}

    if request.method == 'GET':
        return render(request, 'common/admin/setup_site.html', context)

    elif request.method == 'POST':
        if not request.POST.get('type', '') in [t[0] for t in Site.TYPE_CHOICES]:
            raise PermissionDenied

        if not request.POST['domain-type'] in ['fqdn', 'subdomain']:
            raise PermissionDenied

        domain = request.POST['domain'].strip()
        subdomain = domain
        if request.POST['domain-type'] == 'subdomain':
            domain = '%s.test.turistforeningen.no' % domain
        domain = domain.replace('http://', '').rstrip('/')

        if request.POST['type'] == 'forening' and request.active_forening.get_homepage_site() is not None:
            messages.error(request, 'main_site_exists')
            if request.POST['domain-type'] == 'fqdn':
                context['domain'] = domain
            else:
                context['domain'] = subdomain
            return render(request, 'common/admin/setup_site.html', context)

        result = Site.verify_domain(domain)
        if not result['valid']:
            messages.error(request, result['error'])
            if request.POST['domain-type'] == 'fqdn':
                context['domain'] = domain
            else:
                context['domain'] = subdomain
            if result['error'] == 'site_exists':
                context['existing_forening'] = result['existing_forening']
            return render(request, 'common/admin/setup_site.html', context)
        else:
            # TODO let creator choose template?
            site = Site(
                domain=result['domain'],
                prefix=result['prefix'],
                type=request.POST['type'],
                template='large',
                forening=request.active_forening,
                title='',
            )
            if request.POST['type'] == 'kampanje':
                site.title = request.POST['title'].strip()
            site.save()

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

            create_template(request.POST['template'], version)
            request.session.modified = True
            return redirect('admin.views.site_created', site.id)

def site_created(request, site):
    site = Site.objects.get(id=site)
    forside_version = Version.objects.get(
        variant__page__title='Forside',
        variant__page__site=site,
    )
    context = {
        'created_site': site,
        'forside_version': forside_version,
    }
    return render(request, 'common/admin/site_created.html', context)
