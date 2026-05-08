from django.urls import path
from pob import views

urlpatterns = [
    path('',                                                    views.pob_report,          name='pob_report'),
    path('add/',                                                views.pob_add,             name='pob_add'),
    path('<int:pk>/',                                           views.pob_day_detail,      name='pob_day_detail'),
    path('<int:pk>/delete/',                                    views.pob_delete_log,      name='pob_delete_log'),
    path('<int:log_pk>/add-person/',                            views.pob_add_person,      name='pob_add_person'),
    path('person/<int:pk>/edit/',                               views.pob_edit_person,     name='pob_edit_person'),
    path('person/<int:pk>/delete/',                             views.pob_delete_person,   name='pob_delete_person'),
    path('masters/',                                            views.pob_masters,         name='pob_masters'),
    path('masters/<str:master_type>/save/',                     views.pob_master_save,     name='pob_master_save'),
    path('masters/<str:master_type>/<int:pk>/delete/',          views.pob_master_delete,   name='pob_master_delete'),
    path('export/',  views.pob_report_export, name='pob_report_export'),
    path('api/rooms/',                                          views.pob_api_rooms,       name='pob_api_rooms'),
    path('api/employees/',                                      views.pob_api_employees,   name='pob_api_employees'),
    path('employees/',                                          views.pob_employees,       name='pob_employees'),
    path('employees/save/',                                     views.pob_employee_save,   name='pob_employee_save'),
    path('employees/<int:pk>/delete/',                          views.pob_employee_delete, name='pob_employee_delete'),
]
