from django.core.paginator import Paginator
from aktiviteter.models import AktivitetDate

HITS_PER_PAGE = 20

def filter_aktivitet_dates(filter):

    hits = AktivitetDate.get_published().exclude(
        aktivitet__hidden=True
    ).order_by(
        '-start_date'
    )

    paginator = Paginator(hits, HITS_PER_PAGE)
    aktivitet_dates = paginator.page(filter['index'])
    return aktivitet_dates
