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


class OrderSerializer(serializers.ModelSerializer):
    table = TableSerializer()
    menu_items = MenuSerializer(many=True)
    waiter = WaiterSerializer()

    class Meta:
        model = Order
        fields = [
            "id",
            "table",
            "menu_items",
            "waiter",
            "created_at",
            "updated_at",
        ]


class BillSerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    class Meta:
        model = Bill
        fields = [
            "id",
            "order",
            "total_amount",
            "is_paid",
            "created_at",
            "updated_at",
        ]


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
