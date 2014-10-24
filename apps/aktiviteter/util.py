from datetime import datetime
import json

from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage

from aktiviteter.models import AktivitetDate

HITS_PER_PAGE = 20

def filter_aktivitet_dates(filter):

    dates = AktivitetDate.get_published().filter(aktivitet__private=False)

    if 'search' in filter and len(filter['search']) > 2:
        # @TODO add search on aktivitet__code
        dates = dates.filter(aktivitet__title__contains=filter['search'])

    if 'categories' in filter and len(filter['categories']) > 0:
        dates = dates.filter(aktivitet__category__in=filter['categories'])

    if 'difficulties' in filter and len(filter['difficulties']) > 0:
        dates = dates.filter(aktivitet__difficulty__in=filter['difficulties'])

    try:
        if 'start_date' in filter and filter['start_date'] != '':
            dates = dates.filter(start_date__gte=datetime.strptime(filter['start_date'], "%d.%m.%Y"))
        else:
            dates = dates.filter(start_date__gte=datetime.now())

        if 'end_date' in filter and filter['end_date'] != '':
            dates = dates.filter(end_date__lte=datetime.strptime(filter['end_date'], "%d.%m.%Y"))
    except (ValueError, KeyError):
        pass

    if 'organizers' in filter:
        foreninger = []
        cabins = []
        for organizer in filter['organizers']:
            type, id = organizer.split(':')
            if type == 'forening':
                foreninger.append(id)
            elif type == 'cabin':
                cabins.append(id)

        if len(foreninger) > 0:
            dates = dates.filter(
                Q(aktivitet__forening__in=foreninger) |
                Q(aktivitet__co_foreninger__in=foreninger)
            )

        if len(cabins) > 0:
            dates = dates.filter(
                Q(aktivitet__forening_cabin__in=cabins) |
                Q(aktivitet__co_foreninger_cabin__in=cabins)
            )

    dates = dates.order_by(
        '-start_date'
    )

    dates = list(dates)

    # Programmatical filters - due to storing JSON etc. Maybe this could be done in the
    # DB with postgres? Or maybe it should be remodelled?

    if 'audiences' in filter and len(filter['audiences']) > 0:
        dates_to_remove = []
        for date in dates:
            if not any(a in filter['audiences'] for a in json.loads(date.aktivitet.audiences)):
                dates_to_remove.append(date)
        for d in dates_to_remove:
            dates.remove(d)

    if 'locations' in filter and len(filter['locations']) > 0:
        filter['locations'] = [int(l) for l in filter['locations']]
        dates_to_remove = []
        for date in dates:
            if not any(l in filter['locations'] for l in json.loads(date.aktivitet.locations)):
                dates_to_remove.append(date)
        for d in dates_to_remove:
            dates.remove(d)

    paginator = Paginator(dates, HITS_PER_PAGE)

    # Parse "special" values
    page = filter['page']
    if page == 'min':
        page = 1
    elif page == 'max':
        page = paginator.num_pages

    try:
        aktivitet_dates = paginator.page(page)
    except EmptyPage:
        aktivitet_dates = paginator.page(1)
    return aktivitet_dates
