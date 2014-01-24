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
    widget = parse_widget(request, json.loads(request.POST['content']))
    context = RequestContext(request, {'widget': widget})
    return HttpResponse(render_to_string(widget['template'], context))

def save(request, version):
    version = Version.objects.get(id=version)
    response = {
        'new_content_ids': [],
        'unexpected_content_ids': [],
    }

    for row in json.loads(request.POST['rows']):
        obj = Row.objects.get(id=row['id'])
        obj.order = row['order']
        obj.save()

    for column in json.loads(request.POST['columns']):
        obj = Column.objects.get(id=column['id'])
        obj.order = column['order']
        obj.save()

        # Remove contained elements that aren't there client-side
        # If any code in this project should ever be bug-free, it's this.
        # Do NOT do this *after* creating new content elements
        Content.objects.filter(column=obj).exclude(id__in=column['contained_elements']).delete()

    for content in json.loads(request.POST['contents']):
        def create_new_content(content):
            column = Column.objects.get(id=content['column'])
            obj = Content(
                column=column,
                content=content['content'],
                type=content['type'],
                order=content['order'])
            obj.save()
            return obj

        if 'id' in content:
            try:
                # Existing element - update it
                obj = Content.objects.get(id=content['id'])
                obj.order = content['order']
                obj.content = content['content']
                obj.save()
            except Content.DoesNotExist:
                # Whoops, it didn't exist! We'll choose to think that the user is right, and the element
                # should be created, since they have it client-side and are trying to save it.
                # This might happen if two users are editing the same version of a page; one user removes
                # an element and saves, and then the other user saves *her* version, which will try to update
                # a non-existing element.
                new_obj = create_new_content(content)

                # The client will need to update the client-side ID for this element
                response['unexpected_content_ids'].append({
                    'old_id': content['id'],
                    'new_id': new_obj.id})
        else:
            # Send the generated ID to the client
            new_obj = create_new_content(content)
            response['new_content_ids'].append(new_obj.id)

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
            new_parent = Page.on(request.session['active_forening'].site).get(id=request.POST['parent'])
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
