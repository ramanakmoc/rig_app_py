from django.urls import path
from hsd import views

urlpatterns = [
    path('',                    views.hsd_dashboard,      name='hsd_dashboard'),
    path('receipts/',           views.hsd_receipts,       name='hsd_receipts'),
    path('receipt/add/',        views.hsd_add_receipt,    name='hsd_add_receipt'),
    path('receipt/<int:pk>/del/',views.hsd_delete_receipt,name='hsd_delete_receipt'),
    path('issues/',             views.hsd_issues,         name='hsd_issues'),
    path('issue/add/',          views.hsd_add_issue,      name='hsd_add_issue'),
    path('issue/<int:pk>/edit/', views.hsd_edit_issue, name='hsd_edit_issue'),
    path('issue/<int:pk>/del/', views.hsd_delete_issue,   name='hsd_delete_issue'),
    path('api/last-meter/',        views.hsd_get_last_meter,        name='hsd_last_meter'),
    path('api/entered-equipment/', views.hsd_get_entered_equipment, name='hsd_entered_equipment'),
    path('issue/bulk/',            views.hsd_bulk_issue,            name='hsd_bulk_issue'),
    path('api/entered-equipment/', views.hsd_get_entered_equipment, name='hsd_entered_equipment'),
    path('api/entered-equipment/', views.hsd_get_entered_equipment, name='hsd_entered_equipment'),
    path('stock/',              views.hsd_stock,          name='hsd_stock'),
    path('export/excel/',       views.hsd_export_excel,   name='hsd_export_excel'),
    path('export/pdf/',         views.hsd_export_pdf,     name='hsd_export_pdf'),
    path('api/stock-balance/',  views.hsd_api_stock_balance, name='hsd_api_stock_balance'),
    path('api/update-opening/',  views.hsd_api_update_opening, name='hsd_api_update_opening'),
    path('stock/<int:pk>/edit/',   views.hsd_edit_stock,   name='hsd_edit_stock'),
    path('stock/<int:pk>/delete/', views.hsd_delete_stock, name='hsd_delete_stock'),
]
