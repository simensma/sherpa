from django import template
from django.template.defaulttags import url as django_url
from django.template.base import Node
from django.conf import settings
from django.utils.encoding import smart_text
from django.core.urlresolvers import NoReverseMatch

from core.models import Site

register = template.Library()

class PathURLNode(Node):
    def __init__(self, urlnode):
        self.urlnode = urlnode

    def render(self, context):
        try:
            prefix = context['site'].prefix
            return '%s%s' % ('/%s' % prefix if prefix != '' else '', self.urlnode.render(context))
        except NoReverseMatch as e:
            try:
                # Try rendering for main site.
                # Set the needed urlnode variables from the underlying node.
                self.view_name = self.urlnode.view_name
                self.args = self.urlnode.args
                self.kwargs = self.urlnode.kwargs
                self.asvar = self.urlnode.asvar
                return self.render_for_mainsite(context)
            except NoReverseMatch:
                # Raise the original exception
                raise e

    def render_for_mainsite(self, context):
        """
        This is a monkeypatch of Djangos URLNode.render() which uses the 'main' urlconf.
        Don't really like monkeypatching, but we need this functionality for cross-site URLs.
        The alternative would be to manually link to URLs without using the url tag.
        This will need to be upgraded when Django is upgraded. Patched lines are commented.
        See https://github.com/django/django/blob/1.6.2/django/template/defaulttags.py#L415
        """
        from django.core.urlresolvers import reverse, NoReverseMatch
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_text(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        view_name = self.view_name.resolve(context)

        if not view_name:
            raise NoReverseMatch("'url' requires a non-empty first argument. "
                "The syntax changed in Django 1.5, see the docs.")

        # Try to look up the URL twice: once given the view name, and again
        # relative to what we guess is the "main" app. If they both fail,
        # re-raise the NoReverseMatch unless we're using the
        # {% url ... as var %} construct in which case return nothing.
        url = ''
        try:
            # [Sherpa] The following line is monkeypatched (edited).
            url = reverse(view_name, args=args, kwargs=kwargs, current_app=context.current_app, urlconf='sherpa.urls_main')
        except NoReverseMatch as e:
            if settings.SETTINGS_MODULE:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                try:
                    url = reverse(project_name + '.' + view_name,
                              args=args, kwargs=kwargs,
                              current_app=context.current_app)
                except NoReverseMatch:
                    if self.asvar is None:
                        # Re-raise the original exception, not the one with
                        # the path relative to the project. This makes a
                        # better error message.
                        raise e
            else:
                if self.asvar is None:
                    raise e

        # [Sherpa] The following line is monkeypatched (added).
        url = "http://%s%s" % (Site.objects.get(id=1).domain, url)

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url

@register.tag
def url(parser, token):
    return PathURLNode(django_url(parser, token))
