from datetime import datetime, date
import re

from django.shortcuts import render, redirect
from django.core.cache import cache
from django.db.models import Q
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from lxml import etree
import requests

# This ugly import hack imports the model from views because of namespace collision,
# should be 'from aktiviteter.models import Aktivitet'
from aktiviteter.views import Aktivitet
from focus.models import Actor
from page.models import Menu, Page, Variant, Version
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
            main_forening_id__in=[f.focus_id for f in request.active_forening.get_main_foreninger()],
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
        Q(co_foreninger=request.active_forening),
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
        except (requests.ConnectionError, AttributeError):
            pass

        cache.set('admin.betablog', betablog, 60 * 60 * 12)

    context = {
        'betablog': betablog,
        'dashboard_stats': dashboard_stats,
    }
    return render(request, 'common/admin/dashboard.html', context)

def setup_site(request):
    if not request.user.is_admin_in_forening(request.active_forening):
        return render(request, 'common/admin/setup_site_disallowed.html')

    available_site_types = []
    for t in Site.TYPE_CHOICES:
        # The forening type choice shouldn't be available if the current site already has a homepage site
        if t[0] == 'forening':
            if request.active_forening.get_homepage_site() is not None:
                continue
        elif t[0] == 'mal':
            if not request.user.has_perm('sherpa_admin'):
                continue
        available_site_types.append(t)

    context = {'available_site_types': available_site_types}

    if request.method == 'GET':
        return render(request, 'common/admin/setup_site.html', context)

    elif request.method == 'POST':
        if not request.POST.get('type', '') in [t[0] for t in Site.TYPE_CHOICES]:
            raise PermissionDenied

        if request.POST['type'] == 'mal' and not request.user.has_perm('sherpa_admin'):
            raise PermissionDenied

        if not request.POST['domain-type'] in ['fqdn', 'subdomain']:
            raise PermissionDenied

        domain = request.POST['domain'].strip().lower()
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
                context['existing_domain'] = domain
            return render(request, 'common/admin/setup_site.html', context)
        else:
            site = Site(
                domain=result['domain'],
                prefix=result['prefix'],
                type=request.POST['type'],
                template='local',
                forening=request.active_forening,
                title='',
            )
            if request.POST['type'] in ['hytte', 'kampanje']:
                site.title = request.POST['title'].strip()
            site.save()

            # Invalidate the forening's homepage site cache
            cache.delete('forening.homepage_site.%s' % request.active_forening.id)

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

            create_template(request.POST['template'], version)
            request.session.modified = True
            return redirect('admin.views.site_created', site.id)

def site_created(request, site):
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
    return render(request, 'common/admin/site_created.html', context)
