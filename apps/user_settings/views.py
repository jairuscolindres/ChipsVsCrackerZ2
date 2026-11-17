from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import UserSettings
from labs.models import Solve


@login_required
def settings_view(request):
    settings, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        settings.dark_mode = request.POST.get('dark_mode') == 'on'
        settings.email_notifications = request.POST.get('email_notifications') == 'on'

        settings.save()
        messages.success(request, 'Hardware peripheral preferences saved to EEPROM.')
        return redirect('settings:settings')

    total_user_points = Solve.objects.filter(player=request.user).aggregate(total=Sum('points_awarded'))['total'] or 0

    return render(request, 'settings/settings.html', {
        'settings': settings,
        'total_user_points': total_user_points,
    })
