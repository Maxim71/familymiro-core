from django.contrib import admin
from .models import ConstructionObject, SpaceTransferAct, MaterialM15Invoice

@admin.register(ConstructionObject)
class ConstructionObjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address', 'created_at')

@admin.register(SpaceTransferAct)
class SpaceTransferActAdmin(admin.ModelAdmin):
    list_display = ('id', 'construction_object', 'subcontractor_name', 'floor', 'axes', 'chief_approved')
    list_filter = ('chief_approved', 'construction_object')

@admin.register(MaterialM15Invoice)
class MaterialM15InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'act_link', 'material_name', 'quantity', 'unit', 'is_signed_by_chief')
