from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from sherpa.decorators import user_requires_login

from aktiviteter.models import Aktivitet

def index(request):
    aktiviteter = Aktivitet.objects.all().order_by('-start_date')
    context = {'aktiviteter': aktiviteter}
    return render(request, 'common/aktiviteter/index.html', context)

def show(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    context = {'aktivitet': aktivitet}
    return render(request, 'common/aktiviteter/show.html', context)

@user_requires_login()
def join(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    if not aktivitet.accepts_signups():
        raise PermissionDenied
    context = {'aktivitet': aktivitet}
    return render(request, 'common/aktiviteter/join.html', context)

@user_requires_login()
def join_confirm(request, aktivitet):
    aktivitet = Aktivitet.objects.get(id=aktivitet)
    if not aktivitet.accepts_signups():
        raise PermissionDenied
    profile = request.user.get_profile()
    aktivitet.participants.add(profile)
    return HttpResponseRedirect(reverse('aktiviteter.views.show', args=[aktivitet.id]))
