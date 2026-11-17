from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from labs.models import Lab, Solve, Submission


@login_required
def home_view(request):
    user = request.user

    # User solves & points
    user_solves = Solve.objects.filter(player=user).select_related('lab')
    user_solve_lab_ids = set(user_solves.values_list('lab_id', flat=True))
    total_user_points = user_solves.aggregate(total=Sum('points_awarded'))['total'] or 0
    solved_count = user_solves.count()

    total_labs = Lab.objects.filter(is_published=True).count()

    # Global Rank: compute user rank among all users by solve points
    higher_users = (
        Solve.objects.values('player')
        .annotate(total=Sum('points_awarded'))
        .filter(total__gt=total_user_points)
        .count()
    )
    global_rank = higher_users + 1

    # Flag submission accuracy calculation
    total_submissions = Submission.objects.filter(player=user).count()
    correct_submissions = Submission.objects.filter(player=user, is_correct=True).count()
    if total_submissions > 0:
        accuracy = round((correct_submissions / total_submissions) * 100)
    else:
        accuracy = 100 if solved_count > 0 else 0

    # Architecture Badges
    badges = [
        {
            'id': 'esp32',
            'ref': 'U1-MCU',
            'name': 'ESP32-S3 Xtensa',
            'desc': 'Dual-Core 240MHz Virtual IoT Node',
            'tag': 'ESP32',
            'unlocked': any('esp32' in s.lab.title.lower() for s in user_solves)
        },
        {
            'id': 'uart',
            'ref': 'U2-BUS',
            'name': 'UART 115200 8N1',
            'desc': 'Serial Telemetry Bus Snooping',
            'tag': 'UART',
            'unlocked': any('uart' in s.lab.title.lower() for s in user_solves)
        },
        {
            'id': 'i2c',
            'ref': 'U3-I2C',
            'name': 'I2C Peripheral Bus',
            'desc': 'Two-Wire Synchronous Protocol',
            'tag': 'I2C',
            'unlocked': any('i2c' in s.lab.title.lower() for s in user_solves)
        },
        {
            'id': 'spi',
            'ref': 'U4-SPI',
            'name': 'QSPI Flash Memory',
            'desc': 'Non-Volatile Memory Dump',
            'tag': 'SPI',
            'unlocked': any('flash' in s.lab.title.lower() or 'dump' in s.lab.title.lower() for s in user_solves)
        },
        {
            'id': 'logic',
            'ref': 'U5-LA',
            'name': 'Logic Analyzer',
            'desc': 'Digital Waveform Timing Capture',
            'tag': 'PROBE',
            'unlocked': solved_count >= 1
        },
        {
            'id': 'crypto',
            'ref': 'U6-SEC',
            'name': 'Hardware AES-XTS',
            'desc': 'Cryptographic Core Key Pwn',
            'tag': 'CRYPTO',
            'unlocked': total_user_points >= 500
        },
    ]

    # Activity Heatmap: Last 16 weeks (112 days)
    today = datetime.now().date()
    start_date = today - timedelta(days=111)

    solve_dates = {}
    for s in user_solves:
        d_str = s.created_at.date().isoformat()
        solve_dates[d_str] = solve_dates.get(d_str, 0) + 1

    heatmap_weeks = []
    current_week = []

    for i in range(112):
        day_date = start_date + timedelta(days=i)
        d_str = day_date.isoformat()
        count = solve_dates.get(d_str, 0)
        level = 0
        if count == 1:
            level = 1
        elif count == 2:
            level = 2
        elif count >= 3:
            level = 3

        current_week.append({
            'date': d_str,
            'count': count,
            'level': level,
            'weekday': day_date.strftime('%a'),
            'is_today': day_date == today
        })
        if len(current_week) == 7:
            heatmap_weeks.append(current_week)
            current_week = []
    if current_week:
        heatmap_weeks.append(current_week)

    # Recommended target challenges
    recommended_labs = Lab.objects.filter(is_published=True).exclude(id__in=user_solve_lab_ids).order_by('points', 'id')[:3]
    if not recommended_labs.exists():
        recommended_labs = Lab.objects.filter(is_published=True).order_by('points', 'id')[:3]

    # Recent submissions telemetry feed
    recent_submissions = Submission.objects.filter(player=user).select_related('lab').order_by('-created_at')[:6]

    context = {
        'total_user_points': total_user_points,
        'solved_count': solved_count,
        'total_labs': total_labs,
        'global_rank': global_rank,
        'accuracy': accuracy,
        'badges': badges,
        'heatmap_weeks': heatmap_weeks,
        'recommended_labs': recommended_labs,
        'recent_submissions': recent_submissions,
        'user_solve_lab_ids': user_solve_lab_ids,
    }
    return render(request, "home/home.html", context)


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login:login')
    logout(request)
    return redirect('login:login')
