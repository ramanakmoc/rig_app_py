import datetime
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from django.template.loader import render_to_string
from hsd.models import HSDReceipt, HSDIssue, HSDDailyStock
from masters.models import Rig, Vendor, Equipment
from core.decorators import supervisor_required, admin_required


def _get_rigs():
    rigs = list(Rig.objects.values_list('rig_name', flat=True).order_by('rig_name'))
    return rigs if rigs else ['PPE-1', 'PPE-2', 'PPE-3', 'PPE-4', 'PPE-5']


def _build_filter(request, method='GET'):
    data  = request.GET if method == 'GET' else request.POST
    rig_f = data.get('rig', '').strip()
    from_f= data.get('from', '').strip()
    to_f  = data.get('to', datetime.date.today().isoformat()).strip()
    month_f = data.get('month', '').strip()
    return rig_f, from_f, to_f, month_f


def _apply_date_filter(qs, from_f, to_f, month_f):
    if month_f and len(month_f) == 7:
        import calendar
        y, m = month_f.split('-')
        last = calendar.monthrange(int(y), int(m))[1]
        qs = qs.filter(date__gte=f'{month_f}-01', date__lte=f'{month_f}-{last:02d}')
    else:
        if from_f: qs = qs.filter(date__gte=from_f)
        if to_f:   qs = qs.filter(date__lte=to_f)
    return qs


@login_required
def hsd_dashboard(request):
    rig_f, from_f, to_f, month_f = _build_filter(request)

    receipts_qs = _apply_date_filter(HSDReceipt.objects.all(), from_f, to_f, month_f)
    issues_qs   = _apply_date_filter(HSDIssue.objects.all(),   from_f, to_f, month_f)

    if rig_f:
        receipts_qs = receipts_qs.filter(rig=rig_f)
        issues_qs   = issues_qs.filter(rig=rig_f)

    receipt_stats = receipts_qs.aggregate(
        total_received = Sum('quantity_ltrs'),
        total_amount   = Sum('invoice_amount'),
        count          = Count('id'),
    )
    issue_stats = issues_qs.aggregate(
        total_issued = Sum('quantity_ltrs'),
        count        = Count('id'),
    )

    # Per-rig summary
    rig_receipt = receipts_qs.values('rig').annotate(
        received=Sum('quantity_ltrs')).order_by('rig')
    rig_issue = issues_qs.values('rig').annotate(
        issued=Sum('quantity_ltrs')).order_by('rig')

    # Combine rig summaries
    rig_map = {}
    for r in rig_receipt: rig_map[r['rig']] = {'rig': r['rig'], 'received': r['received'], 'issued': 0}
    for r in rig_issue:
        if r['rig'] in rig_map:
            rig_map[r['rig']]['issued'] = r['issued']
        else:
            rig_map[r['rig']] = {'rig': r['rig'], 'received': 0, 'issued': r['issued']}
    for v in rig_map.values():
        v['balance'] = float(v['received'] or 0) - float(v['issued'] or 0)
    rig_summary = sorted(rig_map.values(), key=lambda x: x['rig'])

    # Issue by purpose
    issue_by_purpose = issues_qs.values('purpose').annotate(
        total=Sum('quantity_ltrs'), count=Count('id')
    ).order_by('-total')

    # Latest stock entries
    stock_entries = HSDDailyStock.objects.order_by('-date')[:10]

    return render(request, 'hsd/dashboard.html', {
        'page_title':       'HSD Dashboard',
        'rigs':             _get_rigs(),
        'filters':          {'rig': rig_f, 'from': from_f, 'to': to_f, 'month': month_f},
        'receipt_stats':    receipt_stats,
        'issue_stats':      issue_stats,
        'rig_summary':      rig_summary,
        'issue_by_purpose': issue_by_purpose,
        'stock_entries':    stock_entries,
    })


@login_required
@supervisor_required
def hsd_add_receipt(request):
    rigs    = _get_rigs()
    vendors = Vendor.objects.filter(status='Active').order_by('vendor_name')

    if request.method == 'POST':
        rig           = request.POST.get('rig', '').strip()
        date          = request.POST.get('date', '').strip()
        receipt_no    = request.POST.get('receipt_no', '').strip()
        supplier_id   = request.POST.get('supplier', '').strip()
        supplier_name = request.POST.get('supplier_name', '').strip()
        vehicle_no    = request.POST.get('vehicle_no', '').strip()
        qty           = request.POST.get('quantity_ltrs', '0') or '0'
        rate          = request.POST.get('rate_per_ltr', '').strip() or None
        invoice_amt   = request.POST.get('invoice_amount', '').strip() or None
        received_by   = request.POST.get('received_by', '').strip()
        remarks       = request.POST.get('remarks', '').strip()

        if not rig or not date or float(qty) <= 0:
            messages.error(request, 'Rig, date, and quantity are required.')
            return redirect('hsd_add_receipt')

        supplier_obj = None
        if supplier_id:
            try: supplier_obj = Vendor.objects.get(pk=supplier_id)
            except Vendor.DoesNotExist: pass

        HSDReceipt.objects.create(
            date=date, rig=rig, receipt_no=receipt_no,
            supplier=supplier_obj, supplier_name=supplier_name,
            vehicle_no=vehicle_no, quantity_ltrs=float(qty),
            rate_per_ltr=float(rate) if rate else None,
            invoice_amount=float(invoice_amt) if invoice_amt else None,
            received_by=received_by, remarks=remarks,
            created_by=request.user,
        )
        # Recompute stock for this day
        _recompute_stock(rig, date, request.user)
        messages.success(request, f'Receipt of <strong>{qty} L</strong> recorded for {rig} on {date}.')
        return redirect('hsd_receipts')

    return render(request, 'hsd/add_receipt.html', {
        'page_title': 'Add HSD Receipt',
        'rigs':       rigs,
        'vendors':    vendors,
        'today':      datetime.date.today().isoformat(),
    })


@login_required
@supervisor_required
def hsd_add_issue(request):
    rigs      = _get_rigs()
    equipment = Equipment.objects.filter(status__in=['Available', 'Deployed']).order_by('equipment_type', 'equipment_no')
    purposes  = HSDIssue.PURPOSE_CHOICES

    if request.method == 'POST':
        rig       = request.POST.get('rig', '').strip()
        date      = request.POST.get('date', '').strip()
        purpose   = request.POST.get('purpose', 'Drilling')
        issued_to = request.POST.get('issued_to', '').strip()
        eq_id     = request.POST.get('equipment', '').strip()
        qty       = request.POST.get('quantity_ltrs', '0') or '0'
        issued_by = request.POST.get('issued_by', '').strip()
        remarks   = request.POST.get('remarks', '').strip()

        if not rig or not date or float(qty) <= 0:
            messages.error(request, 'Rig, date, and quantity are required.')
            return redirect('hsd_add_issue')

        eq_obj = None
        if eq_id:
            try: eq_obj = Equipment.objects.get(pk=eq_id)
            except Equipment.DoesNotExist: pass

        HSDIssue.objects.create(
            date=date, rig=rig, purpose=purpose,
            issued_to=issued_to or (str(eq_obj) if eq_obj else ''),
            equipment=eq_obj, quantity_ltrs=float(qty),
            issued_by=issued_by, remarks=remarks,
            created_by=request.user,
        )
        _recompute_stock(rig, date, request.user)
        messages.success(request, f'Issue of <strong>{qty} L</strong> recorded for {issued_to or rig} on {date}.')
        return redirect('hsd_issues')

    return render(request, 'hsd/add_issue.html', {
        'page_title': 'Add HSD Issue',
        'rigs':       rigs,
        'equipment':  equipment,
        'purposes':   purposes,
        'today':      datetime.date.today().isoformat(),
    })


def _recompute_stock(rig, date, user):
    """Auto-create/update HSDDailyStock when receipts or issues change."""
    stock, _ = HSDDailyStock.objects.get_or_create(
        date=date, rig=rig,
        defaults={'created_by': user}
    )
    # Try to carry forward previous day closing stock as opening
    if stock.opening_stock == 0:
        import datetime as dt
        prev_date = (dt.date.fromisoformat(str(date)) - dt.timedelta(days=1)).isoformat()
        prev = HSDDailyStock.objects.filter(date=prev_date, rig=rig).first()
        if prev:
            stock.opening_stock = prev.closing_stock
    stock.recompute()


@login_required
def hsd_receipts(request):
    rig_f, from_f, to_f, month_f = _build_filter(request)
    qs = _apply_date_filter(HSDReceipt.objects.all(), from_f, to_f, month_f)
    if rig_f: qs = qs.filter(rig=rig_f)
    qs = qs.select_related('supplier', 'created_by').order_by('-date', 'rig')

    stats = qs.aggregate(
        total_qty    = Sum('quantity_ltrs'),
        total_amount = Sum('invoice_amount'),
        count        = Count('id'),
    )
    return render(request, 'hsd/receipts.html', {
        'page_title': 'HSD Receipts',
        'receipts':   qs,
        'stats':      stats,
        'rigs':       _get_rigs(),
        'filters':    {'rig': rig_f, 'from': from_f, 'to': to_f, 'month': month_f},
    })


@login_required
def hsd_issues(request):
    rig_f, from_f, to_f, month_f = _build_filter(request)
    qs = _apply_date_filter(HSDIssue.objects.all(), from_f, to_f, month_f)
    if rig_f: qs = qs.filter(rig=rig_f)
    qs = qs.select_related('equipment', 'created_by').order_by('-date', 'rig')

    stats = qs.aggregate(total_qty=Sum('quantity_ltrs'), count=Count('id'))
    by_purpose = qs.values('purpose').annotate(qty=Sum('quantity_ltrs')).order_by('-qty')

    return render(request, 'hsd/issues.html', {
        'page_title': 'HSD Issues',
        'issues':     qs,
        'stats':      stats,
        'by_purpose': by_purpose,
        'rigs':       _get_rigs(),
        'filters':    {'rig': rig_f, 'from': from_f, 'to': to_f, 'month': month_f},
    })


@login_required
def hsd_stock(request):
    rig_f, from_f, to_f, month_f = _build_filter(request)
    qs = _apply_date_filter(HSDDailyStock.objects.all(), from_f, to_f, month_f)
    if rig_f: qs = qs.filter(rig=rig_f)
    qs = qs.order_by('-date', 'rig')

    return render(request, 'hsd/stock.html', {
        'page_title': 'HSD Daily Stock',
        'stock':      qs,
        'rigs':       _get_rigs(),
        'filters':    {'rig': rig_f, 'from': from_f, 'to': to_f, 'month': month_f},
    })


@login_required
@admin_required
def hsd_delete_receipt(request, pk):
    obj = get_object_or_404(HSDReceipt, pk=pk)
    if request.method == 'POST':
        rig, date = obj.rig, obj.date
        obj.delete()
        _recompute_stock(rig, str(date), request.user)
        messages.success(request, 'Receipt deleted.')
    return redirect('hsd_receipts')


@login_required
@admin_required
def hsd_delete_issue(request, pk):
    obj = get_object_or_404(HSDIssue, pk=pk)
    if request.method == 'POST':
        rig, date = obj.rig, obj.date
        obj.delete()
        _recompute_stock(rig, str(date), request.user)
        messages.success(request, 'Issue deleted.')
    return redirect('hsd_issues')


@login_required
def hsd_export_excel(request):
    if request.method != 'POST':
        return redirect('hsd_dashboard')

    rig_f, from_f, to_f, month_f = _build_filter(request, 'POST')
    receipts = _apply_date_filter(HSDReceipt.objects.all(), from_f, to_f, month_f)
    issues   = _apply_date_filter(HSDIssue.objects.all(),   from_f, to_f, month_f)
    stock    = _apply_date_filter(HSDDailyStock.objects.all(), from_f, to_f, month_f)
    if rig_f:
        receipts = receipts.filter(rig=rig_f)
        issues   = issues.filter(rig=rig_f)
        stock    = stock.filter(rig=rig_f)

    wb  = openpyxl.Workbook()
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    NAVY = PatternFill('solid', fgColor='0B3D6D')
    hf   = Font(bold=True, color='FFFFFF', size=10)

    def make_sheet(title, headers, rows_fn):
        ws = wb.create_sheet(title)
        for col, h in enumerate(headers, 1):
            c = ws.cell(1, col, h)
            c.font = hf; c.fill = NAVY
            c.alignment = Alignment(horizontal='center')
            ws.column_dimensions[get_column_letter(col)].width = 14
        ws.row_dimensions[1].height = 25
        for idx, row in enumerate(rows_fn(), 2):
            bg = PatternFill('solid', fgColor='FFFFFF' if idx%2==0 else 'F8FAFC')
            for col, v in enumerate(row, 1):
                cell = ws.cell(idx, col, v)
                cell.fill = bg
                if isinstance(v, datetime.date):
                    cell.number_format = 'DD-MMM-YYYY'

    make_sheet('Receipts',
        ['Date','Rig','Receipt No','Supplier','Vehicle No','Qty (L)','Rate/L','Amount','Remarks'],
        lambda: [(r.date,r.rig,r.receipt_no,r.supplier_name or str(r.supplier or ''),
                  r.vehicle_no,float(r.quantity_ltrs),
                  float(r.rate_per_ltr) if r.rate_per_ltr else '',
                  float(r.invoice_amount) if r.invoice_amount else '',
                  r.remarks) for r in receipts.order_by('date','rig')]
    )
    make_sheet('Issues',
        ['Date','Rig','Purpose','Issued To','Qty (L)','Issued By','Remarks'],
        lambda: [(i.date,i.rig,i.purpose,i.issued_to,float(i.quantity_ltrs),
                  i.issued_by,i.remarks) for i in issues.order_by('date','rig')]
    )
    make_sheet('Stock',
        ['Date','Rig','Opening (L)','Received (L)','Issued (L)','Closing (L)'],
        lambda: [(s.date,s.rig,float(s.opening_stock),float(s.receipts),
                  float(s.consumption),float(s.closing_stock))
                 for s in stock.order_by('date','rig')]
    )

    if 'Sheet' in wb.sheetnames:
        del wb['Sheet']

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="HSD_Report_{datetime.date.today()}.xlsx"'
    wb.save(response)
    return response
