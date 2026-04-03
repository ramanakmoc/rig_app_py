from django.urls import path
from hsd import views

urlpatterns = [
    path('',                    views.hsd_dashboard,      name='hsd_dashboard'),
    path('receipts/',           views.hsd_receipts,       name='hsd_receipts'),
    path('receipt/add/',        views.hsd_add_receipt,    name='hsd_add_receipt'),
    path('receipt/<int:pk>/del/',views.hsd_delete_receipt,name='hsd_delete_receipt'),
    path('issues/',             views.hsd_issues,         name='hsd_issues'),
    path('issue/add/',          views.hsd_add_issue,      name='hsd_add_issue'),
    path('issue/<int:pk>/del/', views.hsd_delete_issue,   name='hsd_delete_issue'),
    path('stock/',              views.hsd_stock,          name='hsd_stock'),
    path('export/excel/',       views.hsd_export_excel,   name='hsd_export_excel'),
]
