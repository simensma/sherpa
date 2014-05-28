from django.shortcuts import render

def index(request, site):
    context = {'site': site}
    return render(request, 'common/admin/sites/index.html', context)
