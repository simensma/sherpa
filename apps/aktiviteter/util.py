from datetime import datetime

from django.db.models import Q
from django.contrib.gis import geos
from django.core.paginator import Paginator, EmptyPage
from django.utils.html import strip_tags
from django.utils.text import truncate_words

from aktiviteter.models import Aktivitet, AktivitetDate

HITS_PER_PAGE = 20

def filter_aktivitet_dates(query):
    filter = query.copy()

    dates = AktivitetDate.get_published().prefetch_related(
        'aktivitet',
        'aktivitet__images',
        'aktivitet__forening',
        'aktivitet__forening__sites',
        'aktivitet__co_foreninger',
    ).filter(aktivitet__private=False)

    if filter.get('search', '') and len(filter['search'].strip()) > 2:
        filter['search'] = filter['search'].split()

        dates = dates.filter(
            Q(reduce(lambda x, y: x & y, [Q(aktivitet__title__icontains=word) | Q(aktivitet__description__icontains=word) for word in filter['search']])) |
            Q(aktivitet__code=filter['search'])
        )

    if filter.get('omrader', ''):
        filter['omrader'] = filter['omrader'].split(',')

        for omrade in filter['omrader']:
            dates = dates.extra(
                where=['%s = ANY ("{0}"."omrader")'.format(Aktivitet._meta.db_table)],
                params=[omrade],
            )

    if filter.get('categories', ''):
        filter['categories'] = filter['categories'].split(',')

        dates = dates.filter(aktivitet__category__in=filter['categories'])

    if filter.get('category_types', ''):
        filter['category_types'] = filter['category_types'].split(',')

        # Note that we're checking for both types and tags, and since objects may have the same tag specified twice,
        # it'll require an explicit distinct clause in our query
        dates = dates.filter(
            Q(aktivitet__category_type__in=filter['category_types']) |
            Q(aktivitet__category_tags__name__in=filter['category_types'])
        )

    if filter.get('audiences', ''):
        filter['audiences'] = filter['audiences'].split(',')

        dates = dates.filter(aktivitet__audiences__name__in=filter['audiences'])

    if filter.get('difficulties', ''):
        filter['difficulties'] = filter['difficulties'].split(',')

        dates = dates.filter(aktivitet__difficulty__in=filter['difficulties'])

    if filter.get('lat_lng', '') and len(filter['lat_lng'].split(',')) == 2:
        filter['lat_lng'] = filter['lat_lng'].split(',')

        # Rule of thumb for buffer; 1 degree is about 100 km
        boundary = geos.Point(float(filter['lat_lng'][0]), float(filter['lat_lng'][1])).buffer(0.5)

        dates = dates.filter(aktivitet__start_point__within=boundary)

    # @TODO refactor to make use of django range query
    # https://docs.djangoproject.com/en/dev/ref/models/querysets/#range
    try:
        if filter.get('start_date', ''):
            dates = dates.filter(start_date__gte=datetime.strptime(filter['start_date'], "%d.%m.%Y"))
        else:
            dates = dates.filter(start_date__gte=datetime.now())

        if filter.get('end_date'):
            dates = dates.filter(end_date__lte=datetime.strptime(filter['end_date'], "%d.%m.%Y"))
    except (ValueError, KeyError):
        pass

    if filter.get('organizers', ''):
        filter['organizers'] = filter['organizers'].split(',')

        foreninger = []
        cabins = []

        for organizer in filter['organizers']:
            type, id = organizer.split(':')
            if type == 'forening':
                foreninger.append(id)
            elif type == 'cabin':
                cabins.append(id)

        if foreninger:
            dates = dates.filter(
                Q(aktivitet__forening__in=foreninger) |
                Q(aktivitet__co_foreninger__in=foreninger)
            )

        if cabins:
            dates = dates.filter(
                Q(aktivitet__forening_cabin__in=cabins) |
                Q(aktivitet__co_foreninger_cabin__in=cabins)
            )

    dates = dates.distinct().order_by(
        'start_date'
    )

    return filter, dates

def paginate_aktivitet_dates(filter, dates):
    paginator = Paginator(dates, HITS_PER_PAGE)

    # Parse "special" values
    page = filter.get('page', 1)
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

