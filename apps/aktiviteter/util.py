from aktiviteter.models import AktivitetDate

HITS_PER_PAGE = 20

def filter_aktivitet_dates(filter):

    start_index = filter['index'] * HITS_PER_PAGE
    end_index = (filter['index'] * HITS_PER_PAGE) + HITS_PER_PAGE

    hits = AktivitetDate.get_published().exclude(
        aktivitet__hidden=True
    ).order_by(
        '-start_date'
    )
    aktivitet_dates = hits[start_index:end_index]
    end_reached = len(hits) <= end_index

    return (aktivitet_dates, end_reached, len(hits))
