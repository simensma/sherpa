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

    # Parse "special" values
    page = filter['page']
    if page == 'min':
        page = 1
    elif page == 'max':
        page = paginator.num_pages

    aktivitet_dates = paginator.page(page)
    return aktivitet_dates
