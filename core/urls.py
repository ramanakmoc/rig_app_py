from django.urls import path
from core.views import (
    home,
    dashboard, add_entry, edit_entry, delete_entry,
    report_daily, report_weekly, report_monthly, alerts,
    export_excel, export_pdf_daily, export_pdf_weekly, export_pdf_monthly,
    user_list, profile_view,
)
from core.views.users import create_user, delete_user, reset_password, change_role, assign_rigs

urlpatterns = [
    path('',                      home,              name='home'),
    path('home/',                  home,              name='home'),
    path('dashboard/',            dashboard,         name='dashboard'),
    path('entry/add/',            add_entry,         name='add_entry'),
    path('entry/<int:pk>/edit/',  edit_entry,        name='edit_entry'),
    path('entry/<int:pk>/del/',   delete_entry,      name='delete_entry'),
    path('report/daily/',         report_daily,      name='daily_report'),
    path('report/weekly/',        report_weekly,     name='weekly_report'),
    path('report/monthly/',       report_monthly,    name='monthly_report'),
    path('alerts/',               alerts,            name='alerts'),
    path('export/excel/',         export_excel,      name='export_excel'),
    path('export/pdf/daily/',     export_pdf_daily,  name='export_pdf_daily'),
    path('export/pdf/weekly/',    export_pdf_weekly, name='export_pdf_weekly'),
    path('export/pdf/monthly/',   export_pdf_monthly,name='export_pdf_monthly'),
    path('users/',                user_list,         name='user_list'),
    path('users/create/',         create_user,       name='create_user'),
    path('users/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('users/reset-password/', reset_password,    name='reset_password'),
    path('users/change-role/',    change_role,       name='change_role'),
    path('profile/',              profile_view,      name='profile'),
    path('users/assign-rigs/',    assign_rigs,       name='assign_rigs'),
]
