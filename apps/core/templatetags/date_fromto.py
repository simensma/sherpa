# encoding: utf-8
from django import template
from django.template.defaultfilters import date

register = template.Library()

@register.filter
def date_fromto(date1, date2):
    if date1 == date2:
        # A 1-day event, we only need to show one date
        return date(date1, "j. F Y")
    else:
        # TODO translations
        if date1.month == date2.month and date1.year == date2.year:
            # Same month, display the month only once
            return "%s til %s" % (date(date1, "j."), date(date2, "j. F Y"))
        else:
            return "%s til %s" % (date(date1, "j. F"), date(date2, "j. F Y"))
