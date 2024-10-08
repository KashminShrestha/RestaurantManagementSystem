from rest_framework import serializers
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


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = [
            "id",
            "number",
            "capacity",
            "status",
            "created_at",
            "updated_at",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "created_at", "updated_at"]


class MenuSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Menu
        fields = [
            "id",
            "name",
            "price",
            "category",
            "created_at",
            "updated_at",
        ]


class WaiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waiter
        fields = [
            "id",
            "name",
            "age",
            "created_at",
            "updated_at",
        ]


class ReceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reception
        fields = [
            "id",
            "name",
            "contact_number",
            "created_at",
            "updated_at",
        ]


# OrderSerializer with logic to create Bill after Order is created
class OrderSerializer(serializers.ModelSerializer):
    menu_items = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all(), many=True)

    class Meta:
        model = Order
        fields = ["id", "table", "menu_items", "waiter", "created_at", "updated_at"]

    def create(self, validated_data):
        menu_items_data = validated_data.pop('menu_items', [])
        order = Order.objects.create(**validated_data)

        # Add menu items to the order
        order.menu_items.set(menu_items_data)

        # Bill is auto-generated by the signal
        return order

    def update(self, instance, validated_data):
        menu_items_data = validated_data.pop('menu_items', None)

        # Update the order fields
        instance.table = validated_data.get('table', instance.table)
        instance.waiter = validated_data.get('waiter', instance.waiter)
        instance.save()

        # Update menu items
        if menu_items_data is not None:
            instance.menu_items.set(menu_items_data)

        # The Bill will be auto-updated due to the signal
        return instance


# BillSerializer to display Bill data
class BillSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Bill
        fields = ["id", "order", "total_amount", "is_paid", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        # Update only the is_paid status; total_amount is handled automatically
        instance.is_paid = validated_data.get('is_paid', instance.is_paid)
        instance.save()
        return instance

class ReservationSerializer(serializers.ModelSerializer):
    table = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all())
    capacity = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "table",
            "customer_name",
            "reservation_time",
            "is_confirmed",
            "capacity",
        ]

    def validate(self, data):
        table = data.get("table")
        capacity = data.get("capacity")

        if table and capacity:
            table_instance = Table.objects.get(id=table.id)
            if table_instance.capacity < capacity:
                raise serializers.ValidationError(
                    "Table does not have sufficient capacity."
                )
            if table_instance.status != "Available":
                raise serializers.ValidationError("Table is not available.")

        return data

    def create(self, validated_data):
        table = validated_data.get("table")
        table_instance = Table.objects.get(id=table.id)

        # Reserve the table
        table_instance.status = "Reserved"
        table_instance.save()

        return super().create(validated_data)
