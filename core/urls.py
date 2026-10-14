# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path
from storage_control import views
from storage_control import products_box
from storage_control import blogger_box

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index_vancouver, name="index_vancouver"),
    path("pto/", views.pto_cabinet_view, name="pto_cabinet"),
    path("docs/infrastructure", views.infrastructure_docs_view),
    path("api/v5/openpyxl-parser/", products_box.verify_ezhik_certificates_api, name="openpyxl_parser"),
    path("api/v5/products/catalog/", products_box.get_syndicate_catalog_api),
    path("api/v5/products/warehouse/", products_box.execute_warehouse_operation_api), 
    path("api/v5/blogger/<str:blogger_id>/", blogger_box.get_blogger_panel_api),
    path("api/users-groups/", views.users_groups_matrix, name="users_groups"),
]
