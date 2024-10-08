from django.contrib import admin
from .models import (
    Table,
    Category,
    Menu,
    Waiter,
    Reception,
    Order,
    Bill,
    Reservation,
)


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ["number", "capacity", "status"]
    list_filter = ["status"]
    search_fields = ["number"]
    list_per_page = 20


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    list_per_page = 20


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "category"]
    list_filter = ["category"]
    search_fields = ["name", "category__name"]
    autocomplete_fields = ["category"]
    list_per_page = 20


@admin.register(Waiter)
class WaiterAdmin(admin.ModelAdmin):
    list_display = ["name", "age"]
    list_per_page = 20


@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_number"]
    list_per_page = 20


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["table", "waiter"]
    list_filter = ["waiter"]
    search_fields = ["table__number", "waiter__name"]
    filter_horizontal = ("menu_items",)  # Allows for multi-select in admin
    list_per_page = 20

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ["order", "total_amount", "is_paid"]
    list_filter = ["is_paid"]
    search_fields = ["order__id"]
    list_per_page = 20


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        "table",
        "customer_name",
        "reservation_time",
        "is_confirmed",
    ]
    list_filter = ["is_confirmed"]
    search_fields = ["table__number", "customer_name"]
    list_per_page = 20
