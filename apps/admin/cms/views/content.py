from __future__ import absolute_import

from django.http import HttpResponse
from django.template import RequestContext, loader

from page.models import Page, Version, Row, Column, Content
from page.widgets import parse_widget
from user.models import Profile
from core.models import Tag

from datetime import datetime
import json

def add(request):
    if request.is_ajax():
        column = Column.objects.get(id=request.POST['column'])
        for content in Content.objects.filter(column=column, order__gte=request.POST['order']):
            content.order = content.order + 1
            content.save()
        content = Content(column=column, content=request.POST['content'], type=request.POST['type'],
            order=request.POST['order'])
        content.save()
        if content.type == 'html' or content.type == 'image':
            result = content.content
        else:
            widget = parse_widget(request, json.loads(content.content))
            t = loader.get_template(widget['template'])
            c = RequestContext(request, {'widget': widget})
            result = t.render(c)
        return HttpResponse(json.dumps({'id': content.id, 'content': result, 'json': content.content}))

def delete(request, content):
    if request.is_ajax():
        try:
            content = Content.objects.get(id=content)
            content.delete()
        except Content.DoesNotExist:
            # Ignore; it's being deleted anyway
            pass
        return HttpResponse()

def update_widget(request, widget):
    widget = Content.objects.get(id=widget)
    widget.content = request.POST['content']
    widget.save()
    widget = parse_widget(request, json.loads(widget.content))
    t = loader.get_template(widget['template'])
    c = RequestContext(request, {'widget': widget})
    result = t.render(c)
    return HttpResponse(json.dumps({'content': result, 'json': request.POST['content']}))

def save(request, version):
    version = Version.objects.get(id=version)
    response = {}

    # Content
    for row in json.loads(request.POST['rows']):
        obj = Row.objects.get(id=row['id'])
        obj.order = row['order']
        obj.save()
    for column in json.loads(request.POST['columns']):
        obj = Column.objects.get(id=column['id'])
        obj.order = column['order']
        obj.save()
    for content in json.loads(request.POST['contents']):
        obj = Content.objects.get(id=content['id'])
        obj.order = content['order']
        obj.content = content['content']
        obj.save()

    # Article/Page data
    if version.variant.page is not None:
        page = version.variant.page

        ### Title ###
        page.title = request.POST['title']

        ### Parent page ###
        if request.POST['parent'] == '':
            new_parent = None
        else:
            new_parent = Page.on(request.session['active_association'].site).get(id=request.POST['parent'])
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
        datetime_string = request.POST["datetime"]
        status = json.loads(request.POST["status"])

        #date format is this one (dd.mm.yyyy hh:mm)
        try:
            date_object = datetime.strptime(datetime_string, '%d.%m.%Y %H:%M')
        except:
            #datetime could not be parsed, this means the field was empty(default) or corrupted, use now()
            date_object = None

        page.published = status
        if date_object is None:
            page.pub_date = datetime.now()
        else:
            page.pub_date = date_object

        version.save()
        page.save()

    elif version.variant.article is not None:
        article = version.variant.article

        ### Authors ###
        publisher_list = json.loads(request.POST['authors'])
        if len(publisher_list) > 0:
            publishers = Profile.objects.filter(id__in=publisher_list)
            version.publishers = publishers
        else:
            response['author_error'] = 'no_authors'

        ### Published state ###
        datetime_string = request.POST["datetime"]
        status =  json.loads(request.POST["status"])

        #date format is this one (dd.mm.yyyy hh:mm)
        try:
            date_object = datetime.strptime(datetime_string, '%d.%m.%Y %H:%M')
        except:
            #datetime could not be parsed, this means the field was empty(default) or corrupted, use now()
            date_object = None

        article.published = status
        if date_object is None:
            article.pub_date = datetime.now()
        else:
            article.pub_date = date_object

        ### Tags ###
        tag_objects = []
        for tag in json.loads(request.POST['tags']):
            try:
                tag_obj = Tag.objects.get(name__iexact=tag)
            except Tag.DoesNotExist:
                tag_obj = Tag(name=tag)
                tag_obj.save()
            tag_objects.append(tag_obj)
        version.tags = tag_objects

        version.save()
        article.save()

    return HttpResponse(json.dumps(response))
