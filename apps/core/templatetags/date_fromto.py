# encoding: utf-8
from django import template
from django.template.defaultfilters import date
from django.utils.translation import ugettext as _

register = template.Library()

@register.filter
def date_fromto(date1, date2):
    if date1.date() == date2.date():
        # A 1-day event, we only need to show one date
        return date(date1, "j. F Y")
    else:
        if date1.month == date2.month and date1.year == date2.year:
            # Same month, display the month only once
            return "%s %s %s" % (date(date1, "j."), _('til'), date(date2, "j. F Y"))
        else:
            return "%s %s %s" % (date(date1, "j. F"), _('til'), date(date2, "j. F Y"))
