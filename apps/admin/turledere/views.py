from django.shortcuts import render

from user.models import Profile

def index(request):
    turledere = Profile.objects.filter(turleder__isnull=False).distinct().prefetch_related('turleder', 'turleder__association')
    turledere = sorted(list(turledere), key=lambda p: p.get_actor().get_full_name())

    context = {
        'turledere': turledere
    }
    return render(request, 'common/admin/turledere/index.html', context)
