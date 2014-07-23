from __future__ import absolute_import

from datetime import datetime
import json

from django.http import HttpResponse
from django.db import transaction
from django.core.cache import cache

from page.models import Page, Version, Row, Column, Content
from page.widgets.util import render_widget
from user.models import User
from core.models import Tag, Site

def reload_raw_widget(request, site):
    active_site = Site.objects.get(id=site)
    return HttpResponse(render_widget(
        request,
        json.loads(request.POST['content']),
        active_site,
        raw=True,
        admin_context=True,
    ))

def save(request, site, version):
    active_site = Site.objects.get(id=site)
    version = Version.objects.get(id=version)
    response = {}

    # Wrap the entire save operation in an atomic transaction
    with transaction.commit_on_success():

        # Delete all existing rows
        version.rows.all().delete()

        posted_rows = json.loads(request.POST['rows'])

        for row in posted_rows:
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
                new_parent = Page.on(active_site).get(id=request.POST['parent'])
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

            cache.delete('content.version.%s' % version.id)

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

            ### Thumbnail state ###
            if request.POST['thumbnail'] == 'none':
                article.thumbnail = None
                article.hide_thumbnail = True
            elif request.POST['thumbnail'] == 'default':
                # Verify server-side that there's at least one image
                image_content = False
                for row in posted_rows:
                    for column in row['columns']:
                        if any(content['type'] == 'image' for content in column['contents']):
                            image_content = True
                            break

                if not image_content:
                    response['thumbnail_missing_image'] = True
                    article.thumbnail = None
                    article.hide_thumbnail = True
                else:
                    article.thumbnail = None
                    article.hide_thumbnail = False
            elif request.POST['thumbnail'] == 'specified':
                article.thumbnail = request.POST['thumbnail_url']
                article.hide_thumbnail = False

            # Record the modification
            article.modified_by = request.user
            article.modified_date = datetime.now()

            version.save()
            article.save()

            cache.delete('articles.%s' % article.id)
            cache.delete('version.%s.thumbnail.small' % version.id)
            cache.delete('version.%s.thumbnail.medium' % version.id)

    return HttpResponse(json.dumps(response))
