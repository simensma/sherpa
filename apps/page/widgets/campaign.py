from datetime import datetime

from page.widgets.widget import Widget
from admin.models import Campaign

class CampaignWidget(Widget):
    core_menu = [
        {'name': None, 'url': '/'}, # Name will default to the campaign title when displayed
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
        now = datetime.now()
        active_campaign = None
        widget_context = {}

        if widget_options.get('display_core_menu'):
            widget_context.update({
                'display_core_menu': True,
                'core_menu': CampaignWidget.core_menu,
            })

        for campaign in widget_options['campaigns']:
            start_date = datetime.strptime(campaign['start_date'], "%d.%m.%Y")
            stop_date = datetime.strptime("%s 23:59:59" % campaign['stop_date'], "%d.%m.%Y %H:%M:%S")

            if widget_options['hide_when_expired'] and now >= start_date and now <= stop_date:
                active_campaign = campaign
            elif not widget_options['hide_when_expired'] and now >= start_date:
                active_campaign = campaign

        if active_campaign is not None:
            widget_context['campaign'] = Campaign.objects.get(id=active_campaign['campaign_id'])

        return widget_context

    def admin_context(self):
        return {'campaigns': Campaign.objects.all()}
