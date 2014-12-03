from datetime import date

from django.db.models import Q

from page.widgets.widget import Widget
from aktiviteter.models import Aktivitet, AktivitetDate, AktivitetAudience
from foreninger.models import Forening

class AktivitetListingWidget(Widget):
    def parse(self, widget_options, site):
        aktivitet_dates = AktivitetDate.get_published().filter(
            Q(aktivitet__forening__in=widget_options['foreninger']) |
            Q(aktivitet__co_foreninger__in=widget_options['foreninger']),
            aktivitet__private=False,
            start_date__gte=date.today(),
        )

        # Skip if none, or all, audiences were chosen
        if len(widget_options['audiences']) > 0 and len(widget_options['audiences']) < len(AktivitetAudience.AUDIENCE_CHOICES):
            aktivitet_dates = aktivitet_dates.filter(aktivitet__audiences__name__in=widget_options['audiences'])

        # Skip if none, or all, categories were chosen
        if len(widget_options['categories']) > 0 and len(widget_options['categories']) < len(Aktivitet.CATEGORY_CHOICES):
            aktivitet_dates = aktivitet_dates.filter(
                aktivitet__category__in=widget_options['categories'],
            )

        aktivitet_dates = aktivitet_dates.order_by('start_date')

        return {'aktivitet_dates': aktivitet_dates}

    def admin_context(self, site):
        return {
            'all_foreninger_sorted': Forening.get_all_sorted_with_type_data(),
            'audiences': AktivitetAudience.AUDIENCE_CHOICES,
            'categories': Aktivitet.CATEGORY_CHOICES,
        }
