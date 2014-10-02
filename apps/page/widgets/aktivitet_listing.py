from page.widgets.widget import Widget
from aktiviteter.util import filter_aktivitet_dates

class AktivitetListingWidget(Widget):
    def parse(self, widget_options, site):
        aktivitet_dates = filter_aktivitet_dates({
            'page': 1,
        })

        return {'aktivitet_dates': aktivitet_dates}
