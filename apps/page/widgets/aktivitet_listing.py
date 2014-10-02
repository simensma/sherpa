from datetime import date

from page.widgets.widget import Widget
from aktiviteter.models import AktivitetDate

class AktivitetListingWidget(Widget):
    def parse(self, widget_options, site):
        aktivitet_dates = AktivitetDate.get_published().filter(
            aktivitet__private=False,
            start_date__gte=date.today(),
        )

        return {'aktivitet_dates': aktivitet_dates}
