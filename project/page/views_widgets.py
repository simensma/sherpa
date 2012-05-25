from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect

from page.models import Version, Row, Column, Content
from articles.models import Article

import json

def parse_content(request, version):
    rows = Row.objects.filter(version=version).order_by('order')
    for row in rows:
        columns = Column.objects.filter(row=row).order_by('order')
        for column in columns:
            contents = Content.objects.filter(column=column).order_by('order')
            for content in contents:
                if content.type == 'widget':
                    content.content = parse_widget(json.loads(content.content))
                elif content.type == 'image':
                    content.content = json.loads(content.content)
            column.contents = contents
        row.columns = columns
    context = {'rows': rows, 'page': version.variant.page}
    return render(request, "page/page.html", context)

# Note: This is also imported by some views in admin, and a view in articles
def parse_widget(widget):
    if(widget['widget'] == "quote"):
        return {'json': json.dumps(widget), 'template': 'widgets/quote/display.html', 'quote': widget['quote'], 'author': widget['author']}
    elif(widget['widget'] == "promo"):
        return {'json': json.dumps(widget), 'template': 'widgets/promo/display.html'}
    elif(widget['widget'] == "editor"):
        article = Article.objects.get(id=widget['article'])
        return {'json': json.dumps(widget), 'template': 'widgets/editor/display.html',
            'static': True,
            'author': article.publisher.user.get_full_name(),
            'email': "TBD",
            'publishdate': article.pub_date}
    elif(widget['widget'] == "articles"):
        versions = Version.objects.filter(
            variant__article__isnull=False, variant__segment__isnull=True,
            variant__article__published=True, active=True
            ).order_by('-variant__article__pub_date')[:widget['count']]
        for version in versions:
            version.load_preview()
        return {'json': json.dumps(widget), 'template': 'widgets/articles/display.html',
                'versions': versions, }
