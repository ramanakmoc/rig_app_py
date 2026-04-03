import datetime
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from core.models import RigDailyLog
from masters.models import Rig


@login_required
def dashboard(request):
    today = datetime.date.today()

    # ── Filter controls ──
    rig_filter  = request.GET.get('rig', '')
    time_filter = request.GET.get('period', 'month')

    if time_filter == 'week':
        date_from    = today - datetime.timedelta(days=6)
        period_label = 'Last 7 Days'
    elif time_filter == 'month':
        date_from    = today.replace(day=1)
        period_label = today.strftime('%B %Y')
    elif time_filter == '3month':
        date_from    = today - datetime.timedelta(days=89)
        period_label = 'Last 3 Months'
    elif time_filter == 'year':
        date_from    = today.replace(month=1, day=1)
        period_label = str(today.year)
    else:  # all
        date_from    = None
        period_label = 'All Time'

    # Base queryset
    qs = RigDailyLog.objects.all()
    if date_from:
        qs = qs.filter(date__gte=date_from, date__lte=today)
    if rig_filter:
        qs = qs.filter(rig=rig_filter)

    # If no data in selected period, fall back to all time
    if not qs.exists() and date_from:
        date_from    = None
        period_label = 'All Time'
        qs = RigDailyLog.objects.all()
        if rig_filter:
            qs = qs.filter(rig=rig_filter)

    # ── Summary stats ──
    stats = qs.aggregate(
        total_op  = Sum('operating_hours'),
        total_sb  = Sum('standby_hours'),
        total_bd  = Sum('breakdown_hours'),
        total_ilm = Sum('ilm_hours'),
        total_zr  = Sum('zero_rate_hours'),
        entries   = Count('id'),
    )
    for k in stats:
        if stats[k] is None:
            stats[k] = 0

    # Fleet efficiency = operating / (op+sb+bd+ilm+zr) * 100
    total_all = (float(stats['total_op']) + float(stats['total_sb']) +
                 float(stats['total_bd']) + float(stats['total_ilm']) +
                 float(stats['total_zr']))
    fleet_efficiency = round(float(stats['total_op']) / total_all * 100, 1) if total_all > 0 else 0

    # Active rig count
    active_rigs_count = Rig.objects.filter(rig_status='Active').count()
    if not active_rigs_count:
        active_rigs_count = qs.values('rig').distinct().count()

    # Days x rigs for efficiency subtitle
    days_count = qs.values('date').distinct().count()
    rigs_count = qs.values('rig').distinct().count()

    # ── Trend chart — daily aggregated ──
    trend_raw = qs.values('date').annotate(
        op  = Sum('operating_hours'),
        sb  = Sum('standby_hours'),
        bd  = Sum('breakdown_hours'),
        ilm = Sum('ilm_hours'),
        zr  = Sum('zero_rate_hours'),
    ).order_by('date')

    trend_labels = [t['date'].strftime('%Y-%m-%d') for t in trend_raw]
    trend_op     = [float(t['op']  or 0) for t in trend_raw]
    trend_sb     = [float(t['sb']  or 0) for t in trend_raw]
    trend_bd     = [float(t['bd']  or 0) for t in trend_raw]
    trend_ilm    = [float(t['ilm'] or 0) for t in trend_raw]
    trend_zr     = [float(t['zr']  or 0) for t in trend_raw]

    # ── Downtime donut — total hours by type ──
    donut_labels = ['Operating', 'Standby', 'Breakdown', 'ILM', 'Zero Rate']
    donut_data   = [
        float(stats['total_op']),
        float(stats['total_sb']),
        float(stats['total_bd']),
        float(stats['total_ilm']),
        float(stats['total_zr']),
    ]

    # ── Per-rig summary ──
    rig_summary = list(qs.values('rig').annotate(
        op_hrs  = Sum('operating_hours'),
        sb_hrs  = Sum('standby_hours'),
        bd_hrs  = Sum('breakdown_hours'),
        ilm_hrs = Sum('ilm_hours'),
        zr_hrs  = Sum('zero_rate_hours'),
        entries = Count('id'),
    ).order_by('rig'))

    for rs in rig_summary:
        for k in ('op_hrs','sb_hrs','bd_hrs','ilm_hrs','zr_hrs'):
            rs[k] = float(rs[k] or 0)
        tot = rs['op_hrs']+rs['sb_hrs']+rs['bd_hrs']+rs['ilm_hrs']+rs['zr_hrs']
        rs['efficiency'] = round(rs['op_hrs'] / tot * 100, 1) if tot > 0 else 0

    # ── All rigs list for filter ──
    all_rigs = list(Rig.objects.values_list('rig_name', flat=True).order_by('rig_name'))
    if not all_rigs:
        all_rigs = list(RigDailyLog.objects.values_list('rig', flat=True).distinct().order_by('rig'))

    # ── Latest entries ──
    latest_entries = RigDailyLog.objects.select_related('created_by').order_by('-date', '-created_at')[:10]

    context = {
        'page_title':        'Dashboard',
        'today':             today,
        'period_label':      period_label,
        'rig_filter':        rig_filter,
        'time_filter':       time_filter,
        'all_rigs':          all_rigs,
        'stats':             stats,
        'fleet_efficiency':  fleet_efficiency,
        'active_rigs_count': active_rigs_count,
        'days_count':        days_count,
        'rigs_count':        rigs_count,
        'rig_summary':       rig_summary,
        'zero_rate_count':   qs.filter(zero_rate_hours__gt=0).count(),
        'latest_entries':    latest_entries,
        # JSON for charts
        'trend_labels_json': json.dumps(trend_labels),
        'trend_op_json':     json.dumps(trend_op),
        'trend_sb_json':     json.dumps(trend_sb),
        'trend_bd_json':     json.dumps(trend_bd),
        'trend_ilm_json':    json.dumps(trend_ilm),
        'trend_zr_json':     json.dumps(trend_zr),
        'donut_labels_json': json.dumps(donut_labels),
        'donut_data_json':   json.dumps(donut_data),
    }
    return render(request, 'core/dashboard.html', context)
