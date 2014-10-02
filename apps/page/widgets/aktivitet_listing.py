from datetime import date

from django.db.models import Q

from page.widgets.widget import Widget
from aktiviteter.models import AktivitetDate
from foreninger.models import Forening

class AktivitetListingWidget(Widget):
    def parse(self, widget_options, site):
        aktivitet_dates = AktivitetDate.get_published().filter(
            Q(aktivitet__forening__in=widget_options['foreninger']) |
            Q(aktivitet__co_foreninger__in=widget_options['foreninger']),
            aktivitet__private=False,
            start_date__gte=date.today(),
        )

        return {'aktivitet_dates': aktivitet_dates}

    def admin_context(self, site):
        return {'all_foreninger_sorted': Forening.get_all_sorted_with_type_data()}
