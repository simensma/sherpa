from datetime import datetime

from django.core.cache import cache

from page.models import Page, Version
from foreninger.models import Forening

def url_picker_context(active_site):
    article_versions = Version.objects.filter(
        variant__article__isnull=False,
        variant__segment__isnull=True,
        variant__article__published=True,
        active=True,
        variant__article__pub_date__lt=datetime.now(),
        variant__article__site=active_site,
    ).order_by('-variant__article__pub_date')

    foreninger_sorted = cache.get('foreninger.all.sorted_by_type')
    if foreninger_sorted is None:
        foreninger_sorted = Forening.sort(Forening.objects.all())
        cache.set('foreninger.all.sorted_by_type', foreninger_sorted, 60 * 60 * 24 * 7)

    return {'url_picker': {
        'pages': Page.on(active_site).order_by('title'),
        'article_versions': article_versions,
        'foreninger': foreninger_sorted,
    }}
