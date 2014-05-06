from __future__ import absolute_import

from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string

from page.models import Page, Version, Row, Column, Content
from page.widgets import parse_widget
from user.models import User
from core.models import Tag

from datetime import datetime
import json

def render_widget(request):
    widget = parse_widget(request, json.loads(request.POST['content']), request.active_forening.site)
    context = RequestContext(request, {'widget': widget})
    return HttpResponse(render_to_string(widget['template'], context))

def save(request, version):
    version = Version.objects.get(id=version)
    response = {
        'new_content_ids': [],
        'unexpected_content_ids': [],
    }

    # Delete all existing rows - a bit scary to do this before creating the new ones in case there's some error
    version.rows.all().delete()

    for row in json.loads(request.POST['rows']):
        row_obj = Row(version=version, order=row['order'])
        row_obj.save()
        for column in row['columns']:
            column_obj = Column(
                row=row_obj,
                span=column['span'],
                offset=column['offset'],
                order=column['order'],
            )
            column_obj.save()
            for content in column['contents']:
                content_obj = Content(
                    column=column_obj,
                    content=content['content'],
                    type=content['type'],
                    order=content['order']
                )
                content_obj.save()

    # Tags - common for pages and articles
    version.tags.clear()
    for tag in [t.lower() for t in json.loads(request.POST['tags'])]:
        obj, created = Tag.objects.get_or_create(name=tag)
        version.tags.add(obj)

    # Article/Page data
    if version.variant.page is not None:
        page = version.variant.page

        ### Title ###
        page.title = request.POST['title']

        ### Parent page ###
        if request.POST['parent'] == '':
            new_parent = None
        else:
            new_parent = Page.on(request.active_forening.site).get(id=request.POST['parent'])
            parent = new_parent
            while parent is not None:
                if parent.id == page.id:
                    response['parent_error'] = 'parent_in_parent'
                    break
                parent = parent.parent
        if 'parent_error' not in response:
            page.parent = new_parent

        ### Ads ###
        version.ads = json.loads(request.POST['ads'])

        ### Published state ###

        try:
            page.published = json.loads(request.POST['status'])
            datetime_string = '%s %s' % (request.POST['publish_date'], request.POST['publish_time'])
            page.pub_date = datetime.strptime(datetime_string, '%d.%m.%Y %H:%M')
        except ValueError:
            if page.published:
                # We're trying to publish, and an error occured.
                if request.POST['publish_date'] == '' and request.POST['publish_time'] == '':
                    # Well, since we didn't specify the date, set it to now - and update it clientside
                    now = datetime.now()
                    response['publish_error'] = 'auto_now'
                    response['publish_date'] = now.strftime('%d.%m.%Y')
                    response['publish_time'] = now.strftime('%H:%M')
                    page.pub_date = now
                else:
                    # Parse error - inform, and don't publish
                    response['publish_error'] = 'unparseable_datetime'
                    page.published = False
            else:
                # An error occured, but we're not publishing so just nullify
                response['publish_error'] = 'error_nullify'
                page.pub_date = None

        # Record the modification
        page.modified_by = request.user
        page.modified_date = datetime.now()

        version.save()
        page.save()

    elif version.variant.article is not None:
        article = version.variant.article

        ### Authors ###
        publisher_list = json.loads(request.POST['authors'])
        if len(publisher_list) > 0:
            publishers = User.get_users().filter(id__in=publisher_list)
            version.publishers = publishers
        else:
            response['author_error'] = 'no_authors'

        ### Published state ###
        try:
            article.published = json.loads(request.POST['status'])
            datetime_string = '%s %s' % (request.POST['publish_date'], request.POST['publish_time'])
            article.pub_date = datetime.strptime(datetime_string, '%d.%m.%Y %H:%M')
        except ValueError:
            if article.published:
                # We're trying to publish, and an error occured.
                if request.POST['publish_date'] == '' and request.POST['publish_time'] == '':
                    # Well, since we didn't specify the date, set it to now - and update it clientside
                    now = datetime.now()
                    response['publish_error'] = 'auto_now'
                    response['publish_date'] = now.strftime('%d.%m.%Y')
                    response['publish_time'] = now.strftime('%H:%M')
                    article.pub_date = now
                else:
                    # Parse error - inform, and don't publish
                    response['publish_error'] = 'unparseable_datetime'
                    article.published = False
            else:
                # An error occured, but we're not publishing so just nullify
                response['publish_error'] = 'error_nullify'
                article.pub_date = None

        # Record the modification
        article.modified_by = request.user
        article.modified_date = datetime.now()

        version.save()
        article.save()

    return HttpResponse(json.dumps(response))
