# -*- coding: utf-8 -*-
from django.urls import path
from . import views

from .views import (
    room_cascade_dynamics_api,
    room_photo_upload_api,
    inventory_foreman_api,
    project_totals_and_analogs_api,
    operation_memo_export_view,
    new_client_wizard_view,
    id_registry_export_view,
    save_object_passport_view,
    room_passport_view,
    stock_movement_create_view, stock_movement_status_view, stock_movement_print_view,
    AdvancedConstructionControlView,
    TrackerSearchAPIView,
    PurchaseRequestAPIView,
    parse_trigger,
    export_staff_excel_view,
    export_customer_gpr_view,
    export_aosr_docx_view,
    mark_passport_view,
    export_dynamic_table_view,
)

app_name = 'storage_control'

urlpatterns = [
    path("partner-league/", views.partner_league_view, name="partner_league"),
    path("api/room-photo-upload/", room_photo_upload_api, name="room_photo_upload_api"),
    path("api/room-cascade-dynamics/", room_cascade_dynamics_api, name="room_cascade_dynamics_api"),
    path("api/inventory-foreman/", inventory_foreman_api, name="inventory_foreman_api"),
    path("api/project-totals/", project_totals_and_analogs_api, name="project_totals_api"),
    path("operation-memo/export/", operation_memo_export_view, name="operation_memo_export"),
    path("new-client/", new_client_wizard_view, name="new_client"),
    path("id-registry/export/", id_registry_export_view, name="id_registry_export"),
    path("api/object-passport/", save_object_passport_view, name="save_object_passport"),
    path("pomeshchenie/<str:room_code>/", room_passport_view, name="room_passport"),
    path("stock-movement/create/", stock_movement_create_view, name="stock_movement_create"),
    path("stock-movement/<int:movement_id>/status/", stock_movement_status_view, name="stock_movement_status"),
    path("stock-movement/<int:movement_id>/print/", stock_movement_print_view, name="stock_movement_print"),
    path('', AdvancedConstructionControlView.as_view(), name='index_family'),
    path('dashboard/', AdvancedConstructionControlView.as_view(), name='dashboard'),
    path('api/tracker-search/', TrackerSearchAPIView.as_view(), name='tracker_search'),
    path('api/purchase-requests/', PurchaseRequestAPIView.as_view(), name='purchase_requests'),
    path('api/parse-trigger/', parse_trigger, name='parse_trigger'),
    path('export/staff-excel/', export_staff_excel_view, name='export_staff_excel'),
    path('export/customer-gpr/', export_customer_gpr_view, name='export_customer_gpr'),
    path('export/aosr/', export_aosr_docx_view, name='export_aosr'),
    path('mark-passport/', mark_passport_view, name='mark_passport'),
    path("export-dynamic-table/", export_dynamic_table_view, name="export_dynamic_table"),
    path("marka/<path:slug>/", views.mark_passport_seo_alias_view, name="mark_passport_seo_alias"),
    path("api/search-async/", views.async_search_api_view, name="async_search_api"),
    path("photo-1c-hub/", views.photo_1c_hub_view, name="photo_1c_hub"),
    path("photo-1c-hub/<int:pk>/accept/", views.photo_1c_accept_view, name="photo_1c_accept"),
    path("photo-1c-hub/<int:pk>/export/<str:fmt>/", views.photo_1c_export_view, name="photo_1c_export"),


]
