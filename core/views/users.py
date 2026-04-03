from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db import transaction
from core.models import UserProfile
from core.decorators import admin_required


VALID_ROLES = ['admin', 'supervisor', 'viewer']


@login_required
@admin_required
def user_list(request):
    users = User.objects.select_related('profile').order_by('id')

    return render(request, 'core/user_list.html', {
        'page_title': 'User Management',
        'users': users,
        'roles': [('admin', 'Admin'), ('supervisor', 'Supervisor'), ('viewer', 'Viewer')],
    })


@login_required
@admin_required
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        role     = request.POST.get('role', 'viewer')

        if role not in VALID_ROLES:
            messages.error(request, 'Invalid role selected.')
            return redirect('user_list')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return redirect('user_list')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists.')
            return redirect('user_list')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('user_list')

        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, password=password)
                profile = user.profile
                profile.role = role
                profile.save()

            messages.success(request, f'User {username} created successfully.')

        except Exception:
            messages.error(request, 'Failed to create user.')

    return redirect('user_list')


@login_required
@admin_required
def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if user == request.user:
        messages.error(request, 'You cannot delete yourself.')
    else:
        user.delete()
        messages.success(request, f'User {user.username} deleted.')

    return redirect('user_list')


@login_required
@admin_required
def reset_password(request):
    if request.method == 'POST':
        uid      = request.POST.get('uid')
        password = request.POST.get('new_password', '').strip()

        user = get_object_or_404(User, pk=uid)

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            user.set_password(password)
            user.save()
            messages.success(request, f'Password reset for {user.username}.')

    return redirect('user_list')


@login_required
@admin_required
def change_role(request):
    if request.method == 'POST':
        uid  = request.POST.get('uid')
        role = request.POST.get('role', 'viewer')

        if role not in VALID_ROLES:
            messages.error(request, 'Invalid role selected.')
            return redirect('user_list')

        user = get_object_or_404(User, pk=uid)

        if user == request.user:
            messages.error(request, 'You cannot change your own role.')
        else:
            profile = user.profile
            profile.role = role
            profile.save()
            messages.success(request, f'Role updated for {user.username}.')

    return redirect('user_list')


@login_required
def profile_view(request):
    if request.method == 'POST':
        current  = request.POST.get('current_password', '')
        new_pwd  = request.POST.get('new_password', '')
        confirm  = request.POST.get('confirm_password', '')

        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
        elif len(new_pwd) < 6:
            messages.error(request, 'New password must be at least 6 characters.')
        elif new_pwd != confirm:
            messages.error(request, 'Passwords do not match.')
        elif new_pwd == current:
            messages.error(request, 'New password must differ from current password.')
        else:
            request.user.set_password(new_pwd)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully.')

        return redirect('profile')

    from core.models import RigDailyLog

    recent = RigDailyLog.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:10]

    return render(request, 'core/profile.html', {
        'page_title': 'My Profile',
        'recent': recent,
    })