from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from analytics.models import Visitor, Request, Parameter, Pageview, Segment

def analytics_visitors_list(request):
    visitors = Visitor.objects.all()
    context = {'visitors': visitors}
    return render(request, 'admin/analytics/list_visitors.html', context)

def analytics_requests_list(request, visitor):
    requests = Request.objects.filter(visitor=visitor)
    context = {'requests': requests}
    return render(request, 'admin/analytics/list_requests.html', context)

#def analytics_pageviews_list(request, visitor):
#    pageviews = Pageview.objects.get(visitor=visitor)
#    context = {'pageviews': pageviews}
#    return render(request, 'admin/analytics/list_pageviews.html', context)
