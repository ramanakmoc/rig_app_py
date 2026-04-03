from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from masters.models import Rig, WellLocation, Vendor, Equipment, EquipmentDeployment
from core.decorators import admin_required, supervisor_required


# ─── RIGS ────────────────────────────────────────────────────────────────────

@login_required
@admin_required
def rig_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            name = request.POST.get('rig_name', '').strip().upper()
            if not name:
                messages.error(request, 'Rig name is required.')
            elif Rig.objects.filter(rig_name=name).exists():
                messages.error(request, f'Rig {name} already exists.')
            else:
                Rig.objects.create(rig_name=name)
                messages.success(request, f'Rig <strong>{name}</strong> added.')
            return redirect('rig_list')

        if action == 'update_details':
            pk = request.POST.get('pk')
            rig = get_object_or_404(Rig, pk=pk)
            rig.rig_model         = request.POST.get('rig_model', '').strip()
            rig.rig_type          = request.POST.get('rig_type', '').strip()
            rig.horse_power       = request.POST.get('horse_power') or None
            rig.depth_capacity    = request.POST.get('depth_capacity') or None
            rig.year_commissioned = request.POST.get('year_commissioned') or None
            rig.current_location  = request.POST.get('current_location', '').strip()
            rig.rig_status        = request.POST.get('rig_status', 'Active')
            rig.notes             = request.POST.get('notes', '').strip()
            rig.save()
            messages.success(request, f'Rig {rig.rig_name} details updated.')
            return redirect('rig_list')

        if action == 'delete':
            pk  = request.POST.get('pk')
            rig = get_object_or_404(Rig, pk=pk)
            from core.models import RigDailyLog
            if RigDailyLog.objects.filter(rig=rig.rig_name).exists():
                messages.error(request, f'Cannot delete {rig.rig_name} — it has log entries.')
            else:
                rig.delete()
                messages.success(request, f'Rig deleted.')
            return redirect('rig_list')

    from core.models import RigDailyLog
    from django.db.models import Count, Max
    rigs = Rig.objects.annotate(
        log_count  = Count('rig_name'),
    ).order_by('rig_name')
    # Manually attach counts (Django can't annotate across CharField fk)
    rig_list_data = []
    for rig in Rig.objects.order_by('rig_name'):
        logs = RigDailyLog.objects.filter(rig=rig.rig_name)
        rig_list_data.append({
            'obj':       rig,
            'log_count': logs.count(),
            'last_entry': logs.order_by('-date').values_list('date', flat=True).first(),
        })

    return render(request, 'masters/rigs.html', {
        'page_title':  'Manage Rigs',
        'rigs':        rig_list_data,
        'statuses':    ['Active', 'Standby', 'Breakdown', 'Demobilised'],
    })


# ─── WELL LOCATIONS ───────────────────────────────────────────────────────────

@login_required
@admin_required
def location_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            loc  = request.POST.get('location', '').strip().upper()
            cat  = request.POST.get('category', 'OTHER')
            block= request.POST.get('block', '').strip()
            dist = request.POST.get('district', '').strip()
            notes= request.POST.get('notes', '').strip()
            if not loc:
                messages.error(request, 'Location name required.')
            elif WellLocation.objects.filter(location=loc).exists():
                messages.error(request, f'{loc} already exists.')
            else:
                WellLocation.objects.create(location=loc, category=cat,
                                             block=block, district=dist, notes=notes)
                messages.success(request, f'Location <strong>{loc}</strong> added.')
            return redirect('location_list')

        if action == 'edit':
            pk   = request.POST.get('pk')
            obj  = get_object_or_404(WellLocation, pk=pk)
            obj.location = request.POST.get('location', '').strip().upper()
            obj.category = request.POST.get('category', 'OTHER')
            obj.block    = request.POST.get('block', '').strip()
            obj.district = request.POST.get('district', '').strip()
            obj.status   = request.POST.get('status', 'Active')
            obj.notes    = request.POST.get('notes', '').strip()
            obj.save()
            messages.success(request, 'Location updated.')
            return redirect('location_list')

        if action == 'delete':
            pk = request.POST.get('pk')
            get_object_or_404(WellLocation, pk=pk).delete()
            messages.success(request, 'Location deleted.')
            return redirect('location_list')

    cat_filter = request.GET.get('cat', '')
    qs = WellLocation.objects.all()
    if cat_filter: qs = qs.filter(category=cat_filter)
    qs = qs.order_by('category', 'location')

    from django.db.models import Count
    cat_counts = dict(
        WellLocation.objects.values_list('category').annotate(n=Count('id'))
    )
    categories = [('BWP','Block Well Pad'),('AWP','Area Well Pad'),('MWP','Main Well Pad'),
                  ('NI','New Installation'),('INTERNAL','Internal'),('OTHER','Other')]

    return render(request, 'masters/locations.html', {
        'page_title':  'Manage Locations',
        'locations':   qs,
        'categories':  categories,
        'cat_counts':  cat_counts,
        'cat_filter':  cat_filter,
    })


# ─── VENDORS ─────────────────────────────────────────────────────────────────

@login_required
@admin_required
def vendor_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        def get_vendor_fields(post):
            return {
                'vendor_code':    post.get('vendor_code', '').strip().upper(),
                'vendor_name':    post.get('vendor_name', '').strip(),
                'vendor_type':    post.get('vendor_type', 'General'),
                'contact_person': post.get('contact_person', '').strip(),
                'phone':          post.get('phone', '').strip(),
                'email':          post.get('email', '').strip(),
                'address':        post.get('address', '').strip(),
                'contract_no':    post.get('contract_no', '').strip(),
                'contract_from':  post.get('contract_from') or None,
                'contract_to':    post.get('contract_to') or None,
                'rate_per_day':   float(post['rate_per_day']) if post.get('rate_per_day') else None,
                'notes':          post.get('notes', '').strip(),
            }

        if action == 'add':
            fields = get_vendor_fields(request.POST)
            if not fields['vendor_code'] or not fields['vendor_name']:
                messages.error(request, 'Code and name required.')
            elif Vendor.objects.filter(vendor_code=fields['vendor_code']).exists():
                messages.error(request, f'Code {fields["vendor_code"]} exists.')
            else:
                Vendor.objects.create(**fields)
                messages.success(request, f'Vendor <strong>{fields["vendor_name"]}</strong> added.')
            return redirect('vendor_list')

        if action == 'edit':
            pk     = request.POST.get('pk')
            obj    = get_object_or_404(Vendor, pk=pk)
            fields = get_vendor_fields(request.POST)
            fields['status'] = request.POST.get('status', 'Active')
            for k, v in fields.items():
                setattr(obj, k, v)
            obj.save()
            messages.success(request, 'Vendor updated.')
            return redirect('vendor_list')

        if action == 'delete':
            pk = request.POST.get('pk')
            get_object_or_404(Vendor, pk=pk).delete()
            messages.success(request, 'Vendor deleted.')
            return redirect('vendor_list')

    vendors = Vendor.objects.all().order_by('vendor_name')
    today   = timezone.now().date()
    return render(request, 'masters/vendors.html', {
        'page_title': 'Manage Vendors',
        'vendors':    vendors,
        'today':      today,
        'vendor_types': ['Trailer','Crane','Forklift','Hydra','Generator','General','Both'],
    })


# ─── EQUIPMENT ────────────────────────────────────────────────────────────────

@login_required
@admin_required
def equipment_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        def get_eq_fields(post):
            vid = post.get('vendor')
            return {
                'equipment_no':    post.get('equipment_no', '').strip().upper(),
                'registration_no': post.get('registration_no', '').strip().upper(),
                'equipment_type':  post.get('equipment_type', 'Crane'),
                'make_model':      post.get('make_model', '').strip(),
                'capacity':        post.get('capacity', '').strip(),
                'year_of_mfg':     int(post['year_of_mfg']) if post.get('year_of_mfg') else None,
                'vendor_id':       int(vid) if vid else None,
                'status':          post.get('status', 'Available'),
                'last_service_date': post.get('last_service_date') or None,
                'next_service_date': post.get('next_service_date') or None,
                'notes':           post.get('notes', '').strip(),
            }

        if action == 'add':
            fields = get_eq_fields(request.POST)
            if not fields['equipment_no']:
                messages.error(request, 'Equipment number required.')
            elif Equipment.objects.filter(equipment_no=fields['equipment_no']).exists():
                messages.error(request, f'{fields["equipment_no"]} already exists.')
            else:
                Equipment.objects.create(**fields)
                messages.success(request, f'Equipment <strong>{fields["equipment_no"]}</strong> added.')
            return redirect('equipment_list')

        if action == 'edit':
            pk     = request.POST.get('pk')
            obj    = get_object_or_404(Equipment, pk=pk)
            fields = get_eq_fields(request.POST)
            for k, v in fields.items():
                setattr(obj, k, v)
            obj.save()
            messages.success(request, 'Equipment updated.')
            return redirect('equipment_list')

        if action == 'deploy':
            pk          = request.POST.get('pk')
            deploy_to   = request.POST.get('deployed_to', '').strip()
            deploy_type = request.POST.get('deploy_type', 'Rig')
            start_date  = request.POST.get('start_date', str(timezone.now().date()))
            obj         = get_object_or_404(Equipment, pk=pk)
            # End any current deployment
            obj.deployments.filter(end_date__isnull=True).update(end_date=start_date)
            EquipmentDeployment.objects.create(
                equipment=obj, deploy_type=deploy_type,
                deployed_to=deploy_to, start_date=start_date,
                created_by=request.user,
            )
            obj.status = 'Deployed'
            obj.save()
            messages.success(request, f'{obj.equipment_no} deployed to {deploy_to}.')
            return redirect('equipment_list')

        if action == 'return':
            pk       = request.POST.get('pk')
            end_date = request.POST.get('end_date', str(timezone.now().date()))
            obj      = get_object_or_404(Equipment, pk=pk)
            obj.deployments.filter(end_date__isnull=True).update(end_date=end_date)
            obj.status = 'Available'
            obj.save()
            messages.success(request, f'{obj.equipment_no} returned to yard.')
            return redirect('equipment_list')

        if action == 'delete':
            pk = request.POST.get('pk')
            get_object_or_404(Equipment, pk=pk).delete()
            messages.success(request, 'Equipment deleted.')
            return redirect('equipment_list')

    type_filter   = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    qs = Equipment.objects.select_related('vendor').prefetch_related('deployments').order_by('equipment_type', 'equipment_no')
    if type_filter:   qs = qs.filter(equipment_type=type_filter)
    if status_filter: qs = qs.filter(status=status_filter)

    vendors = Vendor.objects.filter(status='Active').order_by('vendor_name')
    rigs    = list(Rig.objects.values_list('rig_name', flat=True))

    return render(request, 'masters/equipment.html', {
        'page_title':    'Manage Equipment',
        'equipment':     qs,
        'vendors':       vendors,
        'rigs':          rigs,
        'eq_types':      [t[0] for t in Equipment.TYPE_CHOICES],
        'eq_statuses':   [s[0] for s in Equipment.STATUS_CHOICES],
        'deploy_types':  [d[0] for d in EquipmentDeployment.DEPLOY_TYPE_CHOICES],
        'type_filter':   type_filter,
        'status_filter': status_filter,
        'today':         timezone.now().date().isoformat(),
    })
