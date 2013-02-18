from django.shortcuts import render
from django.core.exceptions import PermissionDenied

from membership.models import SMSServiceRequest

def list(request):
    if not request.user.has_perm('user.sherpa_admin'):
        raise PermissionDenied
    sms_requests = SMSServiceRequest.objects.all()
    total_sent = len(sms_requests.filter(blocked=False))
    sms_requests = sms_requests.order_by('-date')
    sms_price = 0.39
    total_cost = sms_price * total_sent
    context = {
        'sms_requests': sms_requests,
        'sms_price': sms_price,
        'total_cost': total_cost,
        'total_sent': total_sent}
    return render(request, 'common/admin/memberid_sms/list.html', context)
