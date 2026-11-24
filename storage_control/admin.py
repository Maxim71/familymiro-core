# -*- coding: utf-8 -*-
import openpyxl
from openpyxl.styles import Font, PatternFill
from django.contrib import admin
from django.http import HttpResponse
from .models import Document, ParsedPage, ItrStaff, WarehouseTmc


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    actions = ['export_registry_xlsx']

    @admin.action(description="📊 Выгрузить реестр томов (Excel)")
    def export_registry_xlsx(self, request, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Реестр томов РД"
        ws.append(["Документ", "Листов в кэше", "Стадия"])

        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", start_color="2F5597")

        for doc in queryset:
            ws.append([doc.title, doc.pages.count(), "РД"])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=registry_rd.xlsx'
        wb.save(response)
        return response


@admin.register(ParsedPage)
class ParsedPageAdmin(admin.ModelAdmin):
    list_display = ('document', 'page_number', 'detected_axes')
    list_filter = ('document',)
    search_fields = ('text', 'detected_axes')


@admin.register(ItrStaff)
class ItrStaffAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'name', 'role_type')
    search_fields = ('name', 'role_type')


@admin.register(WarehouseTmc)
class WarehouseTmcAdmin(admin.ModelAdmin):
    list_display = ('item_code', 'nomenclature', 'stock_balance', 'unit')
    search_fields = ('item_code', 'nomenclature')

from .models import Document, ParsedPage, ItrStaff, WarehouseTmc, PurchaseRequest


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('material_name', 'deficit_qty', 'unit', 'required_qty', 'status', 'document', 'created_at')
    list_filter = ('status', 'document', 'created_at')
    list_editable = ('status',)
    search_fields = ('material_name', 'document__title')
    actions = ['export_purchase_xlsx']

    @admin.action(description="📋 Выгрузить заявку поставщику (Excel)")
    def export_purchase_xlsx(self, request, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Заявка на закупку ТМЦ"
        ws.append(["Наименование материала", "Ед. изм.", "По проекту", "К закупке (дефицит)", "Статус", "Основание (Том РД)"])

        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", start_color="1F497D")

        for item in queryset:
            ws.append([
                item.material_name,
                item.unit,
                float(item.required_qty),
                float(item.deficit_qty),
                item.get_status_display(),
                item.document.title,
                item.document.title if item.document else "—",
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=purchase_request.xlsx'
        wb.save(response)
        return response

from .models import PartnerVendorLead, BimCrossLink

@admin.register(PartnerVendorLead)
class PartnerVendorLeadAdmin(admin.ModelAdmin):
    list_display = ("vendor_name", "contact_email", "region", "category_group", "unit_price_rub", "status", "source_document")
    list_filter = ("status", "region", "category_group")
    search_fields = ("vendor_name", "contact_email", "project_materials")

@admin.register(BimCrossLink)
class BimCrossLinkAdmin(admin.ModelAdmin):
    list_display = ("bim_tag", "source_discipline", "target_discipline", "link_status", "assigned_to", "created_at")
    list_filter = ("link_status", "source_discipline", "target_discipline")
    search_fields = ("bim_tag", "engineering_note")
