import datetime
import io
from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.template.loader import render_to_string
from core.models import RigDailyLog
from hsd.models import HSDIssue, HSDReceipt
from ilm.models import ILMLog


class Command(BaseCommand):
    help = 'Send daily rig performance + HSD + ILM report email with PDFs'

    def handle(self, *args, **kwargs):
        today     = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        date_str  = yesterday.strftime('%d %b %Y')
        recipients = getattr(settings, 'REPORT_RECIPIENTS', [])

        if not recipients:
            self.stdout.write('No recipients configured.')
            return

        # ── Rig Performance ──
        rig_qs = RigDailyLog.objects.filter(date=yesterday)
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

        rig_rows = rig_qs.values('rig').annotate(
            op  = Sum('operating_hours'),
            sb  = Sum('standby_hours'),
            bd  = Sum('breakdown_hours'),
            ilm = Sum('ilm_hours'),
            zr  = Sum('zero_rate_hours'),
        ).order_by('rig')

        # ── HSD ──
        hsd_issued   = HSDIssue.objects.filter(date=yesterday).aggregate(
            total=Sum('quantity_ltrs'), count=Count('id'))
        hsd_received = HSDReceipt.objects.filter(date=yesterday).aggregate(
            total=Sum('quantity_ltrs'), count=Count('id'))

        # ── ILM ──
        ilm_qs = ILMLog.objects.filter(date=yesterday)
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

        ilm_rows = ilm_qs.order_by('rig')

        # ── Build rig table rows ──
        rig_table_rows = ''
        for r in rig_rows:
            op  = float(r['op']  or 0)
            sb  = float(r['sb']  or 0)
            bd  = float(r['bd']  or 0)
            ilm = float(r['ilm'] or 0)
            zr  = float(r['zr']  or 0)
            total = op + sb + bd + ilm + zr
            eff = round((op + ilm) / total * 100, 1) if total > 0 else 0
            color = '#16a34a' if eff >= 80 else '#dc2626'
            rig_table_rows += f'''
            <tr>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0"><strong>{r['rig']}</strong></td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0;color:#1d4ed8">{op}</td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0;color:#f59e0b">{sb}</td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0;color:#dc2626">{bd}</td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0">{ilm}</td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0;color:#dc2626">{zr}</td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0;font-weight:700;color:{color}">{eff}%</td>
            </tr>'''

        # ── Build ILM table rows ──
        ilm_table_rows = ''
        for i in ilm_rows:
            ilm_table_rows += f'''
            <tr>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0"><strong>{i.rig}</strong></td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0">{i.move_status}</td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0">{i.ilm_from_location or "—"} → {i.ilm_to_location or "—"}</td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0">{i.distance_kms or "—"}</td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0">{i.during_ilm_hrs or "—"}</td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0">{i.trailer_reported}</td>
              <td style="padding:8px;border-bottom:1px solid #e2e8f0;color:#dc2626">{i.trailer_loss}</td>
            </tr>'''

        total_op  = float(rig_stats['total_op'])
        total_all = sum(float(rig_stats[k]) for k in ['total_op','total_sb','total_bd','total_ilm','total_zr'])
        fleet_eff = round((total_op + float(rig_stats['total_ilm'])) / total_all * 100, 1) if total_all > 0 else 0
        fleet_color = '#16a34a' if fleet_eff >= 80 else '#dc2626'
        hsd_issued_total   = float(hsd_issued['total']   or 0)
        hsd_received_total = float(hsd_received['total'] or 0)
        hsd_issued_count   = hsd_issued['count']   or 0
        hsd_received_count = hsd_received['count'] or 0

        # ── HTML Email ──
        html = f'''
        <html><body style="font-family:Arial,sans-serif;color:#1e293b;max-width:700px;margin:auto">
          <div style="background:#0b3d6d;color:white;padding:20px;border-radius:8px 8px 0 0">
            <h2 style="margin:0">&#9968; Daily Operations Report</h2>
            <p style="margin:4px 0 0;opacity:0.8">KRISS DRILLING PVT. LTD. &mdash; {date_str}</p>
          </div>
          <div style="padding:20px;background:#f8fafc;border:1px solid #e2e8f0">

            <!-- Summary Cards -->
            <div style="display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap">
              <div style="flex:1;min-width:120px;background:white;padding:12px;border-radius:8px;border-left:4px solid #1d4ed8;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
                <div style="font-size:11px;color:#64748b">ACTIVE RIGS</div>
                <div style="font-size:22px;font-weight:700">{rig_stats['entries']}</div>
              </div>
              <div style="flex:1;min-width:120px;background:white;padding:12px;border-radius:8px;border-left:4px solid #16a34a;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
                <div style="font-size:11px;color:#64748b">OPERATING HRS</div>
                <div style="font-size:22px;font-weight:700;color:#1d4ed8">{total_op}</div>
              </div>
              <div style="flex:1;min-width:120px;background:white;padding:12px;border-radius:8px;border-left:4px solid {fleet_color};box-shadow:0 1px 3px rgba(0,0,0,0.1)">
                <div style="font-size:11px;color:#64748b">FLEET EFFICIENCY</div>
                <div style="font-size:22px;font-weight:700;color:{fleet_color}">{fleet_eff}%</div>
              </div>
              <div style="flex:1;min-width:120px;background:white;padding:12px;border-radius:8px;border-left:4px solid #f59e0b;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
                <div style="font-size:11px;color:#64748b">HSD ISSUED</div>
                <div style="font-size:22px;font-weight:700;color:#f59e0b">{hsd_issued_total} L</div>
              </div>
            </div>

            <!-- Rig Table -->
            <h3 style="color:#0b3d6d;margin-bottom:8px">Rig-wise Performance</h3>
            <table style="width:100%;border-collapse:collapse;background:white;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
              <thead>
                <tr style="background:#0b3d6d;color:white">
                  <th style="padding:10px;text-align:left">Rig</th>
                  <th style="padding:10px">Op Hrs</th>
                  <th style="padding:10px">SB Hrs</th>
                  <th style="padding:10px">BD Hrs</th>
                  <th style="padding:10px">ILM Hrs</th>
                  <th style="padding:10px">Zero Rate</th>
                  <th style="padding:10px">Efficiency</th>
                </tr>
              </thead>
              <tbody>
                {rig_table_rows if rig_table_rows else '<tr><td colspan="7" style="padding:12px;text-align:center;color:#94a3b8">No entries for yesterday</td></tr>'}
              </tbody>
            </table>

            <!-- HSD Table -->
            <h3 style="color:#0b3d6d;margin:20px 0 8px">HSD Diesel Summary</h3>
            <table style="width:100%;border-collapse:collapse;background:white;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
              <thead>
                <tr style="background:#0b3d6d;color:white">
                  <th style="padding:10px;text-align:left">Type</th>
                  <th style="padding:10px">Quantity (L)</th>
                  <th style="padding:10px">Transactions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style="padding:8px;border-bottom:1px solid #e2e8f0"><strong>Received</strong></td>
                  <td style="padding:8px;border-bottom:1px solid #e2e8f0;color:#16a34a;font-weight:700">{hsd_received_total} L</td>
                  <td style="padding:8px;border-bottom:1px solid #e2e8f0">{hsd_received_count}</td>
                </tr>
                <tr>
                  <td style="padding:8px"><strong>Issued</strong></td>
                  <td style="padding:8px;color:#dc2626;font-weight:700">{hsd_issued_total} L</td>
                  <td style="padding:8px">{hsd_issued_count}</td>
                </tr>
              </tbody>
            </table>

            <!-- ILM Table -->
            <h3 style="color:#0b3d6d;margin:20px 0 8px">ILM Summary</h3>
            <div style="display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap">
              <div style="flex:1;min-width:100px;background:white;padding:10px;border-radius:8px;border-left:4px solid #8b5cf6;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
                <div style="font-size:11px;color:#64748b">ILM ENTRIES</div>
                <div style="font-size:18px;font-weight:700">{ilm_stats['total']}</div>
              </div>
              <div style="flex:1;min-width:100px;background:white;padding:10px;border-radius:8px;border-left:4px solid #1d4ed8;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
                <div style="font-size:11px;color:#64748b">ILM HRS</div>
                <div style="font-size:18px;font-weight:700">{float(ilm_stats['hrs'])}</div>
              </div>
              <div style="flex:1;min-width:100px;background:white;padding:10px;border-radius:8px;border-left:4px solid #16a34a;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
                <div style="font-size:11px;color:#64748b">SAVING HRS</div>
                <div style="font-size:18px;font-weight:700;color:#16a34a">{float(ilm_stats['saving'])}</div>
              </div>
              <div style="flex:1;min-width:100px;background:white;padding:10px;border-radius:8px;border-left:4px solid #dc2626;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
                <div style="font-size:11px;color:#64748b">TRAILER LOSS</div>
                <div style="font-size:18px;font-weight:700;color:#dc2626">{ilm_stats['t_loss']}</div>
              </div>
            </div>
            <table style="width:100%;border-collapse:collapse;background:white;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
              <thead>
                <tr style="background:#0b3d6d;color:white">
                  <th style="padding:10px;text-align:left">Rig</th>
                  <th style="padding:10px">Status</th>
                  <th style="padding:10px">Route</th>
                  <th style="padding:10px">Dist(km)</th>
                  <th style="padding:10px">Actual Hrs</th>
                  <th style="padding:10px">Trailers</th>
                  <th style="padding:10px">T.Loss</th>
                </tr>
              </thead>
              <tbody>
                {ilm_table_rows if ilm_table_rows else '<tr><td colspan="7" style="padding:12px;text-align:center;color:#94a3b8">No ILM entries for yesterday</td></tr>'}
              </tbody>
            </table>

            <p style="margin-top:20px;font-size:12px;color:#94a3b8;text-align:center">
              📎 PDF reports attached — Rig Performance, HSD Diesel, ILM<br>
              This is an automated report from KRISS DRILLING Operations System.<br>
              View full report at <a href="https://db.krissdrilling.com" style="color:#0b3d6d">db.krissdrilling.com</a>
            </p>
          </div>
        </body></html>'''

        # ── Plain text ──
        text = f"""Daily Operations Report - {date_str}
KRISS DRILLING PVT. LTD.

FLEET SUMMARY
-------------
Active Rigs   : {rig_stats['entries']}
Operating Hrs : {total_op}
Fleet Eff     : {fleet_eff}%
HSD Issued    : {hsd_issued_total} L
ILM Entries   : {ilm_stats['total']}

View full report: https://db.krissdrilling.com
"""

        # ── Generate PDFs ──
        import weasyprint

        # Daily PDF
        daily_entries_qs = RigDailyLog.objects.filter(date=yesterday).order_by('rig')
        daily_entries = []
        for e in daily_entries_qs:
            total = float(e.total_hours)
            op = float(e.operating_hours)
            ilm = float(e.ilm_hours)
            eff = round((op + ilm) / total * 100, 1) if total > 0 else 0
            e.eff_pct = eff
            e.op_w  = round(op / 24 * 100, 1)
            e.ilm_w = round(ilm / 24 * 100, 1)
            e.sb_w  = round(float(e.standby_hours) / 24 * 100, 1)
            e.bd_w  = round(float(e.breakdown_hours) / 24 * 100, 1)
            e.zr_w  = round(float(e.zero_rate_hours) / 24 * 100, 1)
            daily_entries.append(e)
        from django.db.models import Sum as _SumD
        daily_agg = RigDailyLog.objects.filter(date=yesterday).aggregate(
            total_op=_SumD('operating_hours'), total_bd=_SumD('breakdown_hours'),
            total_ilm=_SumD('ilm_hours'), total_sb=_SumD('standby_hours'),
            total_zr=_SumD('zero_rate_hours'),
        )
        d_op  = float(daily_agg['total_op']  or 0)
        d_ilm = float(daily_agg['total_ilm'] or 0)
        d_all = sum(float(v or 0) for v in daily_agg.values())
        d_eff = round((d_op + d_ilm) / d_all * 100, 1) if d_all > 0 else 0
        daily_html = render_to_string('exports/daily_pdf.html', {
            'entries':   daily_entries,
            'generated': datetime.datetime.now(),
            'filters':   {'from': str(yesterday), 'to': str(yesterday), 'rig': ''},
            'total_op':  d_op,
            'total_bd':  float(daily_agg['total_bd'] or 0),
            'total_ilm': d_ilm,
            'fleet_eff': d_eff,
        })
        daily_pdf = weasyprint.HTML(string=daily_html).write_pdf()

        # HSD PDF — build rig_sections same as hsd_export_pdf view
        from django.db.models import Sum as _Sum
        hsd_r_qs = HSDReceipt.objects.filter(date=yesterday)
        hsd_i_qs = HSDIssue.objects.filter(date=yesterday)
        hsd_rigs = sorted(set(
            list(hsd_r_qs.values_list('rig', flat=True).distinct()) +
            list(hsd_i_qs.values_list('rig', flat=True).distinct())
        ))
        hsd_rig_sections = []
        for rig in hsd_rigs:
            r_qs = hsd_r_qs.filter(rig=rig).order_by('date')
            i_qs = hsd_i_qs.filter(rig=rig).order_by('date', 'purpose')
            total_rcv = float(r_qs.aggregate(t=_Sum('quantity_ltrs'))['t'] or 0)
            total_iss = float(i_qs.aggregate(t=_Sum('quantity_ltrs'))['t'] or 0)
            by_purpose_raw = list(i_qs.values('purpose').annotate(qty=_Sum('quantity_ltrs')).order_by('-qty'))
            for p in by_purpose_raw:
                p['qty'] = float(p['qty'] or 0)
                p['pct'] = round(p['qty'] / total_iss * 100, 1) if total_iss > 0 else 0
            hsd_rig_sections.append({
                'rig':            rig,
                'receipts':       r_qs,
                'issues':         list(i_qs),
                'total_received': total_rcv,
                'total_issued':   total_iss,
                'balance':        total_rcv - total_iss,
                'receipt_count':  r_qs.count(),
                'issue_count':    i_qs.count(),
                'by_purpose':     by_purpose_raw,
            })
        hsd_html = render_to_string('exports/hsd_pdf.html', {
            'rig_sections': hsd_rig_sections,
            'filters':      {'rig': '', 'from': str(yesterday), 'to': str(yesterday), 'month': ''},
            'generated':    datetime.datetime.now(),
        })
        hsd_pdf = weasyprint.HTML(string=hsd_html).write_pdf()

        # ILM PDF
        from django.db.models import Q as DQ
        ilm_html = render_to_string('exports/ilm_pdf.html', {
            'entries':   ilm_qs.prefetch_related('equipment_usage__equipment'),
            'stats':     ilm_stats,
            'generated': datetime.datetime.now(),
            'filters':   {'from': str(yesterday), 'to': str(yesterday)},
        })
        ilm_pdf = weasyprint.HTML(string=ilm_html).write_pdf()

        # ── Send Email ──
        subject = f"Daily Operations Report — {date_str} | KRISS DRILLING"
        msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, recipients)
        msg.attach_alternative(html, "text/html")
        msg.attach(f'Rig_Performance_{yesterday}.pdf', daily_pdf, 'application/pdf')
        msg.attach(f'HSD_Diesel_{yesterday}.pdf',      hsd_pdf,   'application/pdf')
        msg.attach(f'ILM_Report_{yesterday}.pdf',      ilm_pdf,   'application/pdf')
        msg.send()
        self.stdout.write(self.style.SUCCESS(f'Report sent to {recipients}'))
