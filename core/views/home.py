import datetime
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from core.models import RigDailyLog
from hsd.models import HSDReceipt, HSDIssue
from ilm.models import ILMLog
from masters.models import Rig


@login_required
def home(request):
    today     = datetime.date.today()
    month_start = today.replace(day=1)
    yesterday = today - datetime.timedelta(days=1)

    # ── RIG PERFORMANCE (This Month) ──
    rig_qs = RigDailyLog.objects.filter(date__gte=month_start, date__lte=today)
    rig_stats = rig_qs.aggregate(
        total_op  = Sum('operating_hours'),
        total_sb  = Sum('standby_hours'),
        total_bd  = Sum('breakdown_hours'),
        total_ilm = Sum('ilm_hours'),
        total_zr  = Sum('zero_rate_hours'),
        entries   = Count('id'),
    )
    for k in rig_stats:
        if rig_stats[k] is None:
            rig_stats[k] = 0

    total_all = sum(float(rig_stats[k]) for k in ['total_op','total_sb','total_bd','total_ilm','total_zr'])
    fleet_eff = round((float(rig_stats['total_op']) + float(rig_stats['total_ilm'])) / total_all * 100, 1) if total_all > 0 else 0

    # Rig-wise summary
    rig_summary = list(rig_qs.values('rig').annotate(
        op  = Sum('operating_hours'),
        sb  = Sum('standby_hours'),
        bd  = Sum('breakdown_hours'),
        ilm = Sum('ilm_hours'),
        zr  = Sum('zero_rate_hours'),
    ).order_by('rig'))
    for r in rig_summary:
        for k in ('op','sb','bd','ilm','zr'):
            r[k] = float(r[k] or 0)
        tot = r['op']+r['sb']+r['bd']+r['ilm']+r['zr']
        r['efficiency'] = round((r['op']+r['ilm'])/tot*100, 1) if tot > 0 else 0

    # Trend last 7 days
    from django.db.models.functions import TruncDate
    trend_qs = RigDailyLog.objects.filter(
        date__gte=today-datetime.timedelta(days=6)
    ).values('date').annotate(
        op=Sum('operating_hours'), ilm=Sum('ilm_hours')
    ).order_by('date')
    trend_labels = [str(t['date']) for t in trend_qs]
    trend_op     = [float(t['op'] or 0) for t in trend_qs]
    trend_ilm    = [float(t['ilm'] or 0) for t in trend_qs]

    active_rigs = Rig.objects.filter(rig_status='Active').count() or rig_qs.values('rig').distinct().count()

    # HSD 7-day trend
    hsd_trend_qs = HSDReceipt.objects.filter(
        date__gte=today-datetime.timedelta(days=6)
    ).values('date').annotate(received=Sum('quantity_ltrs')).order_by('date')
    hsd_issue_trend_qs = HSDIssue.objects.filter(
        date__gte=today-datetime.timedelta(days=6)
    ).values('date').annotate(issued=Sum('quantity_ltrs')).order_by('date')

    # Build 7-day date range
    date_range = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    hsd_recv_map  = {r['date']: float(r['received'] or 0) for r in hsd_trend_qs}
    hsd_issue_map = {r['date']: float(r['issued']   or 0) for r in hsd_issue_trend_qs}
    hsd_trend_labels   = [str(d) for d in date_range]
    hsd_trend_received = [hsd_recv_map.get(d, 0)  for d in date_range]
    hsd_trend_issued   = [hsd_issue_map.get(d, 0) for d in date_range]

    # ILM 7-day trend
    ilm_trend_qs = ILMLog.objects.filter(
        date__gte=today-datetime.timedelta(days=6)
    ).values('date').annotate(
        hrs=Sum('during_ilm_hrs'),
        moves=Count('id')
    ).order_by('date')
    ilm_trend_map_hrs   = {r['date']: float(r['hrs']   or 0) for r in ilm_trend_qs}
    ilm_trend_map_moves = {r['date']: int(r['moves']   or 0) for r in ilm_trend_qs}
    ilm_trend_labels = [str(d) for d in date_range]
    ilm_trend_hrs    = [ilm_trend_map_hrs.get(d, 0)   for d in date_range]
    ilm_trend_moves  = [ilm_trend_map_moves.get(d, 0) for d in date_range]

    # ── HSD (This Month) ──
    hsd_receipts = HSDReceipt.objects.filter(date__gte=month_start, date__lte=today)
    hsd_issues   = HSDIssue.objects.filter(date__gte=month_start, date__lte=today)
    hsd_receipt_stats = hsd_receipts.aggregate(total=Sum('quantity_ltrs'), count=Count('id'))
    hsd_issue_stats   = hsd_issues.aggregate(total=Sum('quantity_ltrs'), count=Count('id'))
    hsd_received = float(hsd_receipt_stats['total'] or 0)
    hsd_issued   = float(hsd_issue_stats['total'] or 0)
    hsd_balance  = round(hsd_received - hsd_issued, 1)

    # HSD by purpose
    hsd_by_purpose = list(hsd_issues.values('purpose').annotate(
        total=Sum('quantity_ltrs')
    ).order_by('-total')[:5])

    # HSD rig summary
    hsd_rig_map = {}
    for r in hsd_receipts.values('rig').annotate(received=Sum('quantity_ltrs')):
        hsd_rig_map[r['rig']] = {'rig': r['rig'], 'received': float(r['received'] or 0), 'issued': 0}
    for r in hsd_issues.values('rig').annotate(issued=Sum('quantity_ltrs')):
        if r['rig'] in hsd_rig_map:
            hsd_rig_map[r['rig']]['issued'] = float(r['issued'] or 0)
        else:
            hsd_rig_map[r['rig']] = {'rig': r['rig'], 'received': 0, 'issued': float(r['issued'] or 0)}
    for v in hsd_rig_map.values():
        v['balance'] = round(v['received'] - v['issued'], 1)
    hsd_rig_summary = sorted(hsd_rig_map.values(), key=lambda x: x['rig'])

    # ── ILM (This Month) ──
    ilm_qs = ILMLog.objects.filter(date__gte=month_start, date__lte=today)
    ilm_stats = ilm_qs.aggregate(
        total    = Count('id'),
        hrs      = Sum('during_ilm_hrs'),
        extra    = Sum('rig_move_extra_hrs'),
        saving   = Sum('rig_move_saving_hrs'),
        trailers = Sum('trailer_reported'),
        t_loss   = Sum('trailer_loss'),
    )
    for k in ilm_stats:
        if ilm_stats[k] is None:
            ilm_stats[k] = 0

    ilm_rig_summary = list(ilm_qs.values('rig').annotate(
        entries = Count('id'),
        hrs     = Sum('during_ilm_hrs'),
        saving  = Sum('rig_move_saving_hrs'),
        t_loss  = Sum('trailer_loss'),
    ).order_by('rig'))

    recent_ilm = ilm_qs.order_by('-date')[:5]

    context = {
        'page_title':       'Home',
        'today':            today,
        'month_label':      today.strftime('%B %Y'),
        # Rig
        'rig_stats':        rig_stats,
        'fleet_eff':        fleet_eff,
        'active_rigs':      active_rigs,
        'rig_summary':      rig_summary,
        'trend_labels_json':json.dumps(trend_labels),
        'trend_op_json':    json.dumps(trend_op),
        'trend_ilm_json':   json.dumps(trend_ilm),
        # HSD trend
        'hsd_trend_labels_json':   json.dumps(hsd_trend_labels),
        'hsd_trend_received_json': json.dumps(hsd_trend_received),
        'hsd_trend_issued_json':   json.dumps(hsd_trend_issued),
        # ILM trend
        'ilm_trend_labels_json':   json.dumps(ilm_trend_labels),
        'ilm_trend_hrs_json':      json.dumps(ilm_trend_hrs),
        'ilm_trend_moves_json':    json.dumps(ilm_trend_moves),
        # HSD
        'hsd_received':     hsd_received,
        'hsd_issued':       hsd_issued,
        'hsd_balance':      hsd_balance,
        'hsd_by_purpose':   hsd_by_purpose,
        'hsd_rig_summary':  hsd_rig_summary,
        # ILM
        'ilm_stats':        ilm_stats,
        'ilm_rig_summary':  ilm_rig_summary,
        'recent_ilm':       recent_ilm,
    }
    return render(request, 'core/home.html', context)
