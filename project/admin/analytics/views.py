from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from analytics.models import Visitor, Request, Parameter, Pageview, Segment

@login_required
def visitors_list(request):
    visitors = Visitor.objects.all()
    context = {'visitors': visitors}
    return render(request, 'admin/analytics/list_visitors.html', context)

@login_required
def requests_list(request, visitor):
    requests = Request.objects.filter(visitor=visitor)
    context = {'requests': requests}
    return render(request, 'admin/analytics/list_requests.html', context)

#def pageviews_list(request, visitor):
#    pageviews = Pageview.objects.get(visitor=visitor)
#    context = {'pageviews': pageviews}
#    return render(request, 'admin/analytics/list_pageviews.html', context)
