from django.contrib import admin
from .models import (
    Table,
    Category,
    Menu,
    MenuItem,
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


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "get_category"]
    list_filter = ["menu__category"]
    search_fields = ["name", "menu__category__name"]
    autocomplete_fields = ["menu"]
    list_per_page = 20

    def get_category(self, obj):
        return obj.menu.category.name
    get_category.short_description = "Category"  # Changed from "Name" to "Category"



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
    list_display = ["table", "waiter", "total_price"]  # Add total_price here
    list_filter = ["waiter"]
    search_fields = ["table__number", "waiter__name"]
    filter_horizontal = ("menu_items",)  # Allows for multi-select in admin
    list_per_page = 20

    # This method will call calculate_total and show it in the admin interface
    def total_price(self, obj):
        return obj.calculate_total()  # Call the Order model's method

    total_price.short_description = "Total Price"

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
