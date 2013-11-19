from aktiviteter.models import AktivitetDate

def filter_aktivitet_dates(filter):
    aktivitet_dates = AktivitetDate.get_published().exclude(
        aktivitet__hidden=True
    ).order_by(
        '-start_date'
    )
    return aktivitet_dates
