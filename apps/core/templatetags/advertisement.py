from django import template
from django.template.loader import render_to_string

from page.models import AdPlacement

register = template.Library()

@register.simple_tag(takes_context=True)
def advertisement(context, count_view=True, ad_placement=None):
    if ad_placement is None:
        ad_placement = AdPlacement.get_active_ad(site=context['request'].site, count_view=count_view)
    context['advertisement'] = ad_placement
    return render_to_string('common/page/advertisement.html', context)
