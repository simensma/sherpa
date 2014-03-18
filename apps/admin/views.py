from django.shortcuts import render, redirect
from django.core.cache import cache
from django.db.models import Q
from django.contrib import messages

from datetime import datetime, date
from lxml import etree
import requests
import re

# This ugly import hack imports the model from views because of namespace collision,
# should be 'from aktiviteter.models import Aktivitet'
from aktiviteter.views import Aktivitet
from focus.models import Actor
from page.models import Page
from user.models import User
from core.models import Site, SiteTemplate
from foreninger.models import Forening

def index(request):
    total_membership_count = cache.get('admin.total_membership_count')
    local_membership_count = cache.get('admin.local_membership_count.%s' % request.session['active_forening'].id)
    if total_membership_count is None or local_membership_count is None:
        all_members = Actor.all_members()
        total_membership_count = all_members.count()
        local_membership_count = all_members.filter(
            main_forening_id=request.session['active_forening'].get_main_forening().focus_id
        ).count()
        cache.set('admin.total_membership_count', total_membership_count, 60 * 60 * 12)
        cache.set('admin.local_membership_count.%s' % request.session['active_forening'].id, local_membership_count, 60 * 60 * 12)

    turledere = User.objects.filter(turledere__isnull=False).distinct().count()
    if request.session['active_forening'].site is not None:
        pages = Page.on(request.session['active_forening'].site).filter(
            pub_date__lte=datetime.now(),
            published=True
        ).count()
    else:
        pages = None
    aktiviteter = Aktivitet.objects.filter(
        Q(forening=request.session['active_forening']) |
        Q(co_forening=request.session['active_forening']),
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
    if request.session['active_forening'].site is not None:
        return redirect('admin.cms.views.page.list')

    if request.method == 'GET':
        return render(request, 'common/admin/setup_site.html')
    elif request.method == 'POST':
        # Very simple syntax verification
        domain = request.POST['domain'].strip()
        if domain == '' or domain == 'http://' or not domain.startswith('http://') or not '.' in domain:
            messages.error(request, 'malformed')
            return render(request, 'common/admin/setup_site.html', {'domain': domain})

        domain = domain[len('http://'):]
        if domain.endswith('/'):
            domain = domain[:-1]

        if '/' not in domain:
            prefix = ''
        else:
            try:
                # Prefix folder specified
                domain, prefix = domain.split('/')
                # Only allowed for turistforeningen.no
                if domain != 'turistforeningen.no' and domain != 'www.turistforeningen.no':
                    messages.error(request, 'prefix_for_disallowed_domain')
                    return render(request, 'common/admin/setup_site.html', {
                        'domain': "http://%s/%s" % (domain, prefix)
                    })
            except ValueError:
                # More than one subdir specified
                messages.error(request, 'more_than_one_subdir')
                return render(request, 'common/admin/setup_site.html', {
                    'domain': "http://%s/%s" % (domain, prefix)
                })

        if domain.count('.') == 1 and not domain.startswith('www'):
            domain = "www.%s" % domain

        try:
            existing_site = Site.objects.get(domain=domain, prefix=prefix)
            existing_forening = Forening.objects.get(site=existing_site)
            messages.error(request, 'site_exists')
            return render(request, 'common/admin/setup_site.html', {
                'domain': "http://%s/%s" % (domain, prefix),
                'existing_forening': existing_forening
            })
        except Site.DoesNotExist:
            pass

        # TODO let creator choose template?
        large_template = SiteTemplate.objects.get(name='large')
        site = Site(
            domain=domain,
            prefix=prefix,
            template=large_template
        )
        site.save()
        request.session['active_forening'].site = site
        request.session['active_forening'].save()
        request.session.modified = True
        return redirect('admin.cms.views.page.list')
