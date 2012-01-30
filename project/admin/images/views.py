#from django.core.urlresolvers import reverse
#from django.http import HttpResponseRedirect
from django.shortcuts import render

def dashboard(request):
    return render(request, 'admin/images/dashboard.html')
