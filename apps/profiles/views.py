
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Profile
from labs.models import Solve


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.full_name = request.POST.get('full_name', '').strip()
        profile.bio = request.POST.get('bio', '').strip()
        profile.website_url = request.POST.get('website_url', '').strip()

        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']

        profile.save()
        messages.success(request, 'Operator profile telemetry updated successfully.')
        return redirect('profile:profile')

    user_solves = Solve.objects.filter(player=request.user).select_related('lab').order_by('-created_at')
    total_user_points = user_solves.aggregate(total=Sum('points_awarded'))['total'] or 0
    solved_count = user_solves.count()

    return render(request, 'profile/profile.html', {
        'profile': profile,
        'user_solves': user_solves,
        'total_user_points': total_user_points,
        'solved_count': solved_count,
    })
