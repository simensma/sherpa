from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, InvalidPage

from membership.models import SMSServiceRequest

def list(request):
    if not request.user.has_perm('sherpa_admin'):
        raise PermissionDenied
    sms_requests = SMSServiceRequest.objects.all()
    sms_requests_count = SMSServiceRequest.objects.count()
    total_sent = len(sms_requests.filter(memberid__isnull=False, blocked=False))
    sms_requests = sms_requests.order_by('-date')
    sms_price = 0.39
    total_cost = sms_price * total_sent

    paginator = Paginator(sms_requests, 100)
    try:
        sms_requests = paginator.page(request.GET.get('page', 1))
    except InvalidPage:
        sms_requests = paginator.page(1)

    context = {
        'sms_requests_count': sms_requests_count,
        'sms_price': sms_price,
        'total_cost': total_cost,
        'total_sent': total_sent
    }
    return render(request, 'common/admin/memberid_sms/list.html', context)
