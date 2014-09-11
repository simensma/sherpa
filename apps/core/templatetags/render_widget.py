from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def render_widget(context, content, admin_context=False):
    return content.render_widget(context['request'], context['site'], admin_context)
