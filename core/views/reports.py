import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from core.models import RigDailyLog
from masters.models import Rig


def _get_rigs():
    rigs = list(Rig.objects.values_list('rig_name', flat=True).order_by('rig_name'))
    return rigs if rigs else ['PPE-1', 'PPE-2', 'PPE-3', 'PPE-4', 'PPE-5']

def _get_user_rigs(request):
    all_rigs = _get_rigs()
    try:
        return request.user.profile.filter_rigs(all_rigs)
    except Exception:
        return all_rigs


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
    try:
        p = request.user.profile
        if p.role != 'admin':
            assigned = p.get_assigned_rigs()
            if assigned: qs = qs.filter(rig__in=assigned)
    except: pass
    # Filter by user's assigned rigs
    user_rigs = _get_user_rigs(request)
    if len(user_rigs) < len(_get_rigs()):
        qs = qs.filter(rig__in=user_rigs)
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
        'rigs':        _get_user_rigs(request),
        'filters':     filters,
    })


@login_required
def report_weekly(request):
    from django.db.models.functions import TruncWeek

    # Build week choices from existing data
    existing_weeks = RigDailyLog.objects.annotate(w=TruncWeek('date')).values_list('w', flat=True).distinct().order_by('-w')
    seen = set()
    week_choices = []
    for d in existing_weeks:
        key = d.strftime('%Y-%m-%d')
        if key not in seen:
            seen.add(key)
            week_choices.append({'value': key, 'label': d.strftime('%d %b %Y')})

    from_week = request.GET.get('from_week', '').strip()
    to_week   = request.GET.get('to_week', '').strip()
    rig_f     = request.GET.get('rig', '').strip()

    qs = RigDailyLog.objects.all()
    if rig_f:
        qs = qs.filter(rig=rig_f)
    if from_week:
        qs = qs.filter(date__gte=from_week)
    if to_week:
        # to end of that week (6 days after week start)
        import datetime as dt
        end = dt.date.fromisoformat(to_week) + dt.timedelta(days=6)
        qs = qs.filter(date__lte=end)

    filters = {'rig': rig_f, 'from_week': from_week, 'to_week': to_week}

    weekly_raw = list(qs.annotate(week=TruncWeek('date')).values('week', 'rig').annotate(
        op_hrs  = Sum('operating_hours'),
        sb_hrs  = Sum('standby_hours'),
        bd_hrs  = Sum('breakdown_hours'),
        ilm_hrs = Sum('ilm_hours'),
        zr_hrs  = Sum('zero_rate_hours'),
        entries = Count('id'),
    ).order_by('-week', 'rig'))
    for row in weekly_raw:
        for k in ('op_hrs','sb_hrs','bd_hrs','ilm_hrs','zr_hrs'):
            row[k] = float(row[k] or 0)
        total = row['op_hrs']+row['sb_hrs']+row['bd_hrs']+row['ilm_hrs']+row['zr_hrs']
        row['efficiency'] = round((row['op_hrs']+row['ilm_hrs'])/total*100, 1) if total > 0 else 0
    weekly = weekly_raw

    return render(request, 'core/report_weekly.html', {
        'page_title':   'Weekly Report',
        'weekly':       weekly,
        'rigs':         _get_user_rigs(request),
        'filters':      filters,
        'week_choices': week_choices,
    })


@login_required
def report_monthly(request):
    from django.db.models.functions import TruncMonth
    # Build month choices from existing data
    existing_months = RigDailyLog.objects.annotate(m=TruncMonth('date')).values_list('m', flat=True).distinct().order_by('-m')
    seen = set()
    month_choices = []
    for d in existing_months:
        key = d.strftime('%Y-%m')
        if key not in seen:
            seen.add(key)
            month_choices.append({'value': key, 'label': d.strftime('%b %Y')})

    # Handle month filters
    from_month = request.GET.get('from_month', '').strip()
    to_month   = request.GET.get('to_month', '').strip()
    rig_f      = request.GET.get('rig', '').strip()

    qs = RigDailyLog.objects.all()
    if rig_f:
        qs = qs.filter(rig=rig_f)
    if from_month:
        qs = qs.filter(date__gte=datetime.date(int(from_month[:4]), int(from_month[5:7]), 1))
    if to_month:
        import calendar
        y, m = int(to_month[:4]), int(to_month[5:7])
        last_day = calendar.monthrange(y, m)[1]
        qs = qs.filter(date__lte=datetime.date(y, m, last_day))

    filters = {'rig': rig_f, 'from_month': from_month, 'to_month': to_month}

    monthly_raw = list(qs.annotate(month=TruncMonth('date')).values('month', 'rig').annotate(
        op_hrs  = Sum('operating_hours'),
        sb_hrs  = Sum('standby_hours'),
        bd_hrs  = Sum('breakdown_hours'),
        ilm_hrs = Sum('ilm_hours'),
        zr_hrs  = Sum('zero_rate_hours'),
        entries = Count('id'),
    ).order_by('-month', 'rig'))
    for row in monthly_raw:
        for k in ('op_hrs','sb_hrs','bd_hrs','ilm_hrs','zr_hrs'):
            row[k] = float(row[k] or 0)
        total = row['op_hrs']+row['sb_hrs']+row['bd_hrs']+row['ilm_hrs']+row['zr_hrs']
        row['efficiency'] = round((row['op_hrs']+row['ilm_hrs'])/total*100, 1) if total > 0 else 0
    monthly = monthly_raw

    rig_totals = qs.values('rig').annotate(
        op  = Sum('operating_hours'),
        sb  = Sum('standby_hours'),
        bd  = Sum('breakdown_hours'),
        ilm = Sum('ilm_hours'),
    ).order_by('rig')

    return render(request, 'core/report_monthly.html', {
        'page_title':    'Monthly Report',
        'monthly':       monthly,
        'rig_totals':    rig_totals,
        'rigs':          _get_rigs(),
        'filters':       filters,
        'month_choices': month_choices,
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
        'rigs':         _get_user_rigs(request),
        'filters':      filters,
    })
