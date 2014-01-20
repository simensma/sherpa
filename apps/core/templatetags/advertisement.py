from django import template
from django.template.loader import render_to_string

from page.models import AdPlacement

register = template.Library()

@register.simple_tag(takes_context=True)
def advertisement(context, count_view=True):
    context['advertisement'] = AdPlacement.get_active_ad(count_view=count_view)
    return render_to_string('common/page/advertisement.html', context)
