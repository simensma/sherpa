from datetime import datetime

from page.widgets.widget import Widget
from page.models import Version

class ArticlesWidget(Widget):
    def parse(self, widget_options, site):
        versions = Version.objects.filter(
            variant__article__isnull=False,
            variant__segment__isnull=True,
            variant__article__published=True,
            active=True,
            variant__article__pub_date__lt=datetime.now(),
            variant__article__site=site,
        ).order_by('-variant__article__pub_date')

        if len(widget_options['tags']) == 0:
            version_matches = versions
        else:
            # Filter on tags. We'll have to do multiple queries, since we can't make list-lookups with 'icontains'.
            # The alternative would be some sort of advanced regex.
            version_matches = []
            for tag in widget_options['tags']:
                for version in versions.filter(tags__name__icontains=tag):
                    # Drop duplicates manually
                    if not version in version_matches:
                        version_matches.append(version)

            # Now re-apply the date sorting, since picking out matches in the order of the tags will mess that up
            version_matches = sorted(version_matches, key=lambda v: v.variant.article.pub_date, reverse=True)

        if widget_options['layout'] == 'medialist':
            version_matches = version_matches[:int(widget_options['count'])]
            span = None
        else:
            version_matches = version_matches[:int(widget_options['columns'])]
            span = 12 / int(widget_options['columns'])

        return {
            'layout': widget_options['layout'],
            'title': widget_options['title'],
            'display_images': widget_options['display_images'],
            'tag_link': widget_options['tag_link'],
            'versions': version_matches,
            'span': span,
        }
