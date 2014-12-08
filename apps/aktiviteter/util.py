from datetime import datetime
import json

from django.db.models import Q
from django.contrib.gis import geos
from django.core.paginator import Paginator, EmptyPage
from django.utils.html import strip_tags
from django.utils.text import truncate_words

from aktiviteter.models import AktivitetDate

HITS_PER_PAGE = 20

def filter_aktivitet_dates(filter):

    dates = AktivitetDate.get_published().prefetch_related(
        'aktivitet',
        'aktivitet__images',
        'aktivitet__forening',
        'aktivitet__forening__sites',
        'aktivitet__co_foreninger',
    ).filter(aktivitet__private=False)

    if 'search' in filter and len(filter['search']) > 2:
        # @TODO add search on aktivitet__code
        dates = dates.filter(
            Q(aktivitet__title__icontains=filter['search']) |
            Q(aktivitet__description__icontains=filter['search'])
        )

    if 'categories' in filter and len(filter['categories']) > 0:
        dates = dates.filter(aktivitet__category__in=filter['categories'])

    if 'category_types' in filter and len(filter['category_types']) > 0:
        # Note that we're checking for both types and tags, and since objects may have the same tag specified twice,
        # it'll require an explicit distinct clause in our query
        dates = dates.filter(
            Q(aktivitet__category_type__in=filter['category_types']) |
            Q(aktivitet__category_tags__name__in=filter['category_types'])
        )

    if 'audiences' in filter and len(filter['audiences']) > 0:
        dates = dates.filter(aktivitet__audiences__name__in=filter['audiences'])

    if 'difficulties' in filter and len(filter['difficulties']) > 0:
        dates = dates.filter(aktivitet__difficulty__in=filter['difficulties'])

    if 'lat_lng' in filter and len(filter['lat_lng'].split(',')) == 2:
        latlng = filter['lat_lng'].split(',')

        # Rule of thumb for buffer; 1 degree is about 100 km
        boundary = geos.Point(float(latlng[0]), float(latlng[1])).buffer(0.5)

        dates = dates.filter(aktivitet__start_point__within=boundary)

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

    dates = dates.distinct().order_by(
        'start_date'
    )

    dates = list(dates)

    # Programmatical filters - due to storing JSON etc. Maybe this could be done in the
    # DB with postgres? Or maybe it should be remodelled?

    if 'locations' in filter and len(filter['locations']) > 0:
        filter['locations'] = [int(l) for l in filter['locations']]
        dates_to_remove = []
        for date in dates:
            if not any(l in filter['locations'] for l in json.loads(date.aktivitet.locations)):
                dates_to_remove.append(date)
        for d in dates_to_remove:
            dates.remove(d)

    return dates

def paginate_aktivitet_dates(filter, dates):
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

def mapify_aktivitet_dates(filter, dates):
    dates_to_remove = []
    for date in dates:
        if not date.aktivitet.start_point:
            dates_to_remove.append(date)
    for date in dates_to_remove:
        dates.remove(date)

    return [{
        'id': date.aktivitet.id,
        'title': date.aktivitet.title,
        'desc': truncate_words(strip_tags(date.aktivitet.description), 30),
        'lat': date.aktivitet.start_point.get_coords()[0],
        'lng': date.aktivitet.start_point.get_coords()[1],
    } for date in dates]

