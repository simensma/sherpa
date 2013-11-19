from django.core.paginator import Paginator
from aktiviteter.models import AktivitetDate

HITS_PER_PAGE = 20

def filter_aktivitet_dates(filter):

    dates = AktivitetDate.get_published().exclude(aktivitet__hidden=True)

    if 'categories' in filter and len(filter['categories']) > 0:
        dates = dates.filter(aktivitet__category__in=filter['categories'])

    dates = dates.order_by(
        '-start_date'
    )

    paginator = Paginator(dates, HITS_PER_PAGE)

    # Parse "special" values
    page = filter['page']
    if page == 'min':
        page = 1
    elif page == 'max':
        page = paginator.num_pages

    aktivitet_dates = paginator.page(page)
    return aktivitet_dates
