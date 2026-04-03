from django.urls import path
from ilm import views

urlpatterns = [
    path('report/',                          views.ilm_report,          name='ilm_report'),
    path('add/',                             views.ilm_add,             name='ilm_add'),
    path('<int:pk>/edit/',                   views.ilm_edit,            name='ilm_edit'),
    path('<int:pk>/delete/',                 views.ilm_delete,          name='ilm_delete'),
    path('<int:pk>/equipment/add/',          views.ilm_add_equipment,   name='ilm_add_equipment'),
    path('<int:pk>/equipment/<int:eq_pk>/remove/', views.ilm_remove_equipment, name='ilm_remove_equipment'),
    path('import/',                          views.ilm_import,          name='ilm_import'),
    path('export/excel/',                    views.ilm_export_excel,    name='ilm_export_excel'),
    path('export/pdf/',                      views.ilm_export_pdf,      name='ilm_export_pdf'),
]
