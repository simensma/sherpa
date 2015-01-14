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

        url_query_parameters = []
        limit = widget_options.get('limit', 50)
        total = aktivitet_dates.count()
        more_activities_count = total - limit

        # Skip if none, or all, audiences were chosen
        if len(widget_options['audiences']) > 0 and len(widget_options['audiences']) < len(AktivitetAudience.AUDIENCE_CHOICES):
            aktivitet_dates = aktivitet_dates.filter(aktivitet__audiences__name__in=widget_options['audiences'])
            url_query_parameters.append("audiences=%s" % ",".join(widget_options['audiences']))

        # Skip if none, or all, categories were chosen
        if len(widget_options['categories']) > 0 and len(widget_options['categories']) < len(Aktivitet.CATEGORY_CHOICES):
            aktivitet_dates = aktivitet_dates.filter(
                aktivitet__category__in=widget_options['categories'],
            )
            url_query_parameters.append("categories=%s" % ",".join(widget_options['categories']))

        if len(widget_options['foreninger']) > 0:
            organizers = []
            for forening in widget_options['foreninger']:
                organizers.append("forening:%s" % forening)

            url_query_parameters.append("organizers=%s" % ",".join(organizers))

        aktivitet_dates = aktivitet_dates.order_by('start_date')[:limit]
        see_more_query_params = "&".join(url_query_parameters)

        return {
            'aktivitet_dates': aktivitet_dates,
            'see_more_query_params': see_more_query_params,
            'total': total,
            'limit': limit,
            'more_activities_count': more_activities_count
        }

    def admin_context(self, site):
        return {
            'all_foreninger_sorted': Forening.get_all_sorted_with_type_data(),
            'audiences': AktivitetAudience.AUDIENCE_CHOICES,
            'categories': Aktivitet.CATEGORY_CHOICES,
        }
