from django.urls import path
from masters import views

urlpatterns = [
    path('rigs/',       views.rig_list,       name='rig_list'),
    path('locations/',  views.location_list,  name='location_list'),
    path('vendors/',    views.vendor_list,     name='vendor_list'),
    path('equipment/',  views.equipment_list,  name='equipment_list'),
]
