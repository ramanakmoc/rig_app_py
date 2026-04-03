import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from core.models import RigDailyLog
from masters.models import Rig


def _get_rigs():
    rigs = list(Rig.objects.values_list('rig_name', flat=True).order_by('rig_name'))
    return rigs if rigs else ['PPE-1', 'PPE-2', 'PPE-3', 'PPE-4', 'PPE-5']


def _build_filter(request):
    rig_f    = request.GET.get('rig', '').strip()
    from_f   = request.GET.get('from', '').strip()
    to_f     = request.GET.get('to', datetime.date.today().isoformat()).strip()
    status_f = request.GET.get('status', '').strip()

    qs = RigDailyLog.objects.all()
    if rig_f:    qs = qs.filter(rig=rig_f)
    if from_f:   qs = qs.filter(date__gte=from_f)
    if to_f:     qs = qs.filter(date__lte=to_f)
    if status_f: qs = qs.filter(status=status_f)

    return qs, {'rig': rig_f, 'from': from_f, 'to': to_f, 'status': status_f}


@login_required
def report_daily(request):
    qs, filters = _build_filter(request)
    entries = qs.order_by('-date', 'rig').select_related('created_by')

    stats = qs.aggregate(
        total_op  = Sum('operating_hours'),
        total_sb  = Sum('standby_hours'),
        total_bd  = Sum('breakdown_hours'),
        total_ilm = Sum('ilm_hours'),
        total_zr  = Sum('zero_rate_hours'),
        entries   = Count('id'),
    )

    rig_summary = qs.values('rig').annotate(
        op_hrs  = Sum('operating_hours'),
        sb_hrs  = Sum('standby_hours'),
        bd_hrs  = Sum('breakdown_hours'),
        ilm_hrs = Sum('ilm_hours'),
        zr_hrs  = Sum('zero_rate_hours'),
        entries = Count('id'),
    ).order_by('rig')

    return render(request, 'core/report_daily.html', {
        'page_title':  'Daily Report',
        'entries':     entries,
        'stats':       stats,
        'rig_summary': rig_summary,
        'rigs':        _get_rigs(),
        'filters':     filters,
    })


@login_required
def report_weekly(request):
    qs, filters = _build_filter(request)

    # Group by week
    from django.db.models.functions import TruncWeek
    weekly = qs.annotate(week=TruncWeek('date')).values('week', 'rig').annotate(
        op_hrs  = Sum('operating_hours'),
        sb_hrs  = Sum('standby_hours'),
        bd_hrs  = Sum('breakdown_hours'),
        ilm_hrs = Sum('ilm_hours'),
        zr_hrs  = Sum('zero_rate_hours'),
        entries = Count('id'),
    ).order_by('-week', 'rig')

    return render(request, 'core/report_weekly.html', {
        'page_title': 'Weekly Report',
        'weekly':     weekly,
        'rigs':       _get_rigs(),
        'filters':    filters,
    })


@login_required
def report_monthly(request):
    qs, filters = _build_filter(request)

    from django.db.models.functions import TruncMonth
    monthly = qs.annotate(month=TruncMonth('date')).values('month', 'rig').annotate(
        op_hrs  = Sum('operating_hours'),
        sb_hrs  = Sum('standby_hours'),
        bd_hrs  = Sum('breakdown_hours'),
        ilm_hrs = Sum('ilm_hours'),
        zr_hrs  = Sum('zero_rate_hours'),
        entries = Count('id'),
    ).order_by('-month', 'rig')

    # Chart data per rig
    rig_totals = qs.values('rig').annotate(
        op  = Sum('operating_hours'),
        sb  = Sum('standby_hours'),
        bd  = Sum('breakdown_hours'),
        ilm = Sum('ilm_hours'),
    ).order_by('rig')

    return render(request, 'core/report_monthly.html', {
        'page_title': 'Monthly Report',
        'monthly':    monthly,
        'rig_totals': rig_totals,
        'rigs':       _get_rigs(),
        'filters':    filters,
    })


@login_required
def alerts(request):
    qs, filters = _build_filter(request)
    zero_entries = qs.filter(zero_rate_hours__gt=0).order_by('-date', 'rig')

    total_zero = zero_entries.aggregate(total=Sum('zero_rate_hours'))['total'] or 0

    rig_zero = zero_entries.values('rig').annotate(
        total_zr = Sum('zero_rate_hours'),
        days     = Count('id'),
    ).order_by('-total_zr')

    return render(request, 'core/alerts.html', {
        'page_title':   'Zero Rate Alerts',
        'zero_entries': zero_entries,
        'total_zero':   total_zero,
        'rig_zero':     rig_zero,
        'rigs':         _get_rigs(),
        'filters':      filters,
    })
