from datetime import datetime

from page.widgets.widget import Widget
from admin.models import Campaign

class CampaignWidget(Widget):
    def parse(self, widget_options, site):
        now = datetime.now()
        active_campaign = None
        for campaign in widget_options['campaigns']:
            start_date = datetime.strptime(campaign['start_date'], "%d.%m.%Y")
            stop_date = datetime.strptime("%s 23:59:59" % campaign['stop_date'], "%d.%m.%Y %H:%M:%S")

            if widget_options['hide_when_expired'] and now >= start_date and now <= stop_date:
                active_campaign = campaign
            elif not widget_options['hide_when_expired'] and now >= start_date:
                active_campaign = campaign

        if active_campaign is None:
            return {}
        else:
            return {
                'campaign': Campaign.objects.get(id=active_campaign['campaign_id']),
            }

    def admin_context(self):
        return {'campaigns': Campaign.objects.all()}
