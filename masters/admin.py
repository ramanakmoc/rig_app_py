from django.contrib import admin

from .models import Equipment, EquipmentDeployment, Rig, Vendor, WellLocation


@admin.register(Rig)
class RigAdmin(admin.ModelAdmin):
    list_display = ("rig_name", "rig_type", "rig_status", "current_location")
    list_filter = ("rig_status", "rig_type")
    search_fields = ("rig_name", "current_location")


@admin.register(WellLocation)
class WellLocationAdmin(admin.ModelAdmin):
    list_display = ("location", "category", "block", "district", "status")
    list_filter = ("category", "status")
    search_fields = ("location", "block", "district")


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("vendor_code", "vendor_name", "vendor_type", "status", "contract_to")
    list_filter = ("status", "vendor_type")
    search_fields = ("vendor_code", "vendor_name")


class EquipmentDeploymentInline(admin.TabularInline):
    model = EquipmentDeployment
    extra = 0
    fields = ("deploy_type", "deployed_to", "start_date", "end_date")


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("equipment_no", "equipment_type", "make_model", "status", "vendor")
    list_filter = ("equipment_type", "status")
    search_fields = ("equipment_no", "registration_no", "make_model")
    inlines = [EquipmentDeploymentInline]


@admin.register(EquipmentDeployment)
class EquipmentDeploymentAdmin(admin.ModelAdmin):
    list_display = ("equipment", "deploy_type", "deployed_to", "start_date", "end_date")
    list_filter = ("deploy_type",)
    search_fields = ("deployed_to",)
