import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import RigDailyLog
from core.decorators import supervisor_required, admin_required
from masters.models import Rig


def _get_rigs():
    rigs = list(Rig.objects.filter(rig_status='Active').values_list('rig_name', flat=True))
    return rigs if rigs else ['PPE-1', 'PPE-2', 'PPE-3', 'PPE-4', 'PPE-5']

def _get_user_rigs(request):
    """Return only rigs the current user can access."""
    all_rigs = _get_rigs()
    try:
        return request.user.profile.filter_rigs(all_rigs)
    except Exception:
        return all_rigs


@login_required
@supervisor_required
def add_entry(request):
    rigs = _get_user_rigs(request)

    # ? FIX: define today_obj first
    today_obj = datetime.date.today()
    today = today_obj.isoformat()
    yesterday = (today_obj - datetime.timedelta(days=1)).isoformat()

    if request.method == 'POST':
        date    = request.POST.get('date', '').strip()
        rig     = request.POST.get('rig', '').strip()
        op_hrs  = request.POST.get('operating_hours',  '0') or '0'
        sb_hrs  = request.POST.get('standby_hours',    '0') or '0'
        bd_hrs  = request.POST.get('breakdown_hours',  '0') or '0'
        ilm_hrs = request.POST.get('ilm_hours',        '0') or '0'
        zr_hrs  = request.POST.get('zero_rate_hours',  '0') or '0'
        reason  = request.POST.get('reason', '').strip()
        status  = request.POST.get('status', 'Running')

        errors = []

        # Required
        if not date or not rig:
            errors.append('Date and rig are required.')

        # Date validation
        try:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            if date_obj > today_obj:
                errors.append('Future date not allowed.')
        except ValueError:
            errors.append('Invalid date format.')

        # Hours validation
        try:
            total = float(op_hrs)+float(sb_hrs)+float(bd_hrs)+float(ilm_hrs)+float(zr_hrs)
            if total > 24.01:
                errors.append(f'Total hours ({total:.2f}) cannot exceed 24.')
            if total <= 0:
                errors.append('At least one hour type must be greater than 0.')
        except ValueError:
            errors.append('Invalid hour values.')

        # Duplicate check
        if not errors and RigDailyLog.objects.filter(rig=rig, date=date).exists():
            errors.append(f'Entry already exists for {rig} on {date}. Use Edit instead.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'core/add_entry.html', {
                'rigs': rigs,
                'today': today,
                'default_date': yesterday,
                'page_title': 'Add Entry',
                'post': request.POST,
            })

        RigDailyLog.objects.create(
            date=date,
            rig=rig,
            operating_hours=op_hrs,
            standby_hours=sb_hrs,
            breakdown_hours=bd_hrs,
            ilm_hours=ilm_hrs,
            zero_rate_hours=zr_hrs,
            reason=reason,
            status=status,
            created_by=request.user,
        )

        messages.success(request, f'Entry saved for {rig} on {date}.')
        return redirect('daily_report')

    return render(request, 'core/add_entry.html', {
        'rigs': rigs,
        'today': today,
        'default_date': yesterday,  # ? yesterday default
        'page_title': 'Add Entry',
        'post': {},                # ? prevents template crash
    })


@login_required
@supervisor_required
def edit_entry(request, pk):
    entry = get_object_or_404(RigDailyLog, pk=pk)
    rigs  = _get_rigs()

    if request.method == 'POST':
        op_hrs  = request.POST.get('operating_hours',  '0') or '0'
        sb_hrs  = request.POST.get('standby_hours',    '0') or '0'
        bd_hrs  = request.POST.get('breakdown_hours',  '0') or '0'
        ilm_hrs = request.POST.get('ilm_hours',        '0') or '0'
        zr_hrs  = request.POST.get('zero_rate_hours',  '0') or '0'
        reason  = request.POST.get('reason', '').strip()
        status  = request.POST.get('status', 'Running')

        try:
            total = float(op_hrs)+float(sb_hrs)+float(bd_hrs)+float(ilm_hrs)+float(zr_hrs)
            if total > 24.01:
                messages.error(request, f'Total hours ({total:.2f}) cannot exceed 24.')
                return render(request, 'core/edit_entry.html', {
                    'entry': entry, 'rigs': rigs, 'page_title': 'Edit Entry'
                })
        except ValueError:
            messages.error(request, 'Invalid hour values.')
            return render(request, 'core/edit_entry.html', {
                'entry': entry, 'rigs': rigs, 'page_title': 'Edit Entry'
            })

        entry.operating_hours  = op_hrs
        entry.standby_hours    = sb_hrs
        entry.breakdown_hours  = bd_hrs
        entry.ilm_hours        = ilm_hrs
        entry.zero_rate_hours  = zr_hrs
        entry.reason = reason
        entry.status = status
        entry.save()

        messages.success(request, f'Entry updated for {entry.rig} on {entry.date}.')
        return redirect('daily_report')

    return render(request, 'core/edit_entry.html', {
        'entry': entry,
        'rigs': rigs,
        'page_title': 'Edit Entry',
    })


@login_required
@admin_required
def delete_entry(request, pk):
    entry = get_object_or_404(RigDailyLog, pk=pk)
    if request.method == 'POST':
        rig, date = entry.rig, entry.date
        entry.delete()
        messages.success(request, f'Entry for {rig} on {date} deleted.')
    return redirect('daily_report')