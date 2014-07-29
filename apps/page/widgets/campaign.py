from datetime import datetime
import json

from django.core.cache import cache

from page.widgets.widget import Widget
from page.models import Content
from admin.models import Campaign
from core.models import Site

class CampaignWidget(Widget):
    core_menu = [
        {'name': None, 'url': '/'}, # Name will default to the main campaign title when displayed
        {'name': 'Fellesturer', 'url': '/fellesturer/'},
        {'name': 'Hytter og ruter', 'url': '/hytter/'},
        {'name': 'Barn', 'url': '/barn/'},
        {'name': 'Ungdom', 'url': '/ung/'},
        {'name': 'Fjellsport', 'url': '/fjellsport/'},
        {'name': 'Senior', 'url': '/senior/'},
        {'name': 'Skole', 'url': '/skole/'},
        {'name': 'Kurs og utdanning', 'url': '/kurs/'},
        {'name': 'Tur for alle', 'url': '/tur-for-alle/'},
        {'name': 'Turplanlegger', 'url': '/utno/'},
        {'name': 'Fjelltreffen', 'url': '/fjelltreffen/'},
    ]

    def parse(self, widget_options, site):
        widget_context = {}

        if widget_options.get('display_core_menu'):
            widget_context.update({
                'display_core_menu': True,
                'core_menu': CampaignWidget.core_menu,
            })

            # Resolve the main campaign title. We'll have to fetch the Content object from the front page of
            # the main site, find the active campaign, and fetch its title - if it exists.

            # We want to cache this complex lookup, but the invalidation part is slightly tricky. Saves are
            # done on a general basis and if we delete this cache for every page save, it won't really help
            # that much.
            # So what we'll do is cache the Content object ID and verify that it exists. If it doesn't, assume
            # that the front page settings are changed. Note that this works because all page saves always
            # deletes all content and creates new objects, instead of updating existing ones.
            main_campaign = cache.get('widgets.campaign.main_campaign')
            if main_campaign is None or not Content.objects.filter(main_campaign['content_id']).exists():
                main_site = Site.objects.get(id=Site.DNT_CENTRAL_ID)
                main_site_frontpage_widgets = Content.objects.filter(
                    column__row__version__variant__page__site=main_site,
                    column__row__version__variant__page__slug='',
                    type='widget',
                )

                for content in main_site_frontpage_widgets:
                    main_widget_options = json.loads(content.content)
                    if main_widget_options['widget'] == 'campaign':
                        # This is a campaign widget; assume there's only one on the page and fetch its details
                        main_campaign = {
                            'content_id': content.id,
                            'main_widget_options': main_widget_options,
                        }
                        # Note that we're not setting the cache if we didn't find the main campaign - search again instantly
                        cache.set('widgets.campaign.main_campaign_widget', main_campaign, 60 * 60 * 24)

            # Always resolve the active campaign; shouldn't cache this as it varies with time
            if main_campaign is not None:
                main_active_campaign = CampaignWidget.resolve_active_campaign(main_widget_options)
                if main_active_campaign is not None:
                    # All right, there is an active main site front page campaign, get the title
                    widget_context['main_campaign_title'] = Campaign.objects.get(id=main_active_campaign['campaign_id']).title

        active_campaign = CampaignWidget.resolve_active_campaign(widget_options)

        if active_campaign is not None:
            widget_context['campaign'] = Campaign.objects.get(id=active_campaign['campaign_id'])

        return widget_context

    def admin_context(self, site):
        return {'campaigns': Campaign.objects.all()}

    @staticmethod
    def resolve_active_campaign(widget_options):
        active_campaign = None
        now = datetime.now()
        for campaign in widget_options['campaigns']:
            start_date = datetime.strptime(campaign['start_date'], "%d.%m.%Y")
            stop_date = datetime.strptime("%s 23:59:59" % campaign['stop_date'], "%d.%m.%Y %H:%M:%S")

            if widget_options['hide_when_expired'] and now >= start_date and now <= stop_date:
                active_campaign = campaign
            elif not widget_options['hide_when_expired'] and now >= start_date:
                active_campaign = campaign
        return active_campaign
