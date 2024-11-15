from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from .models import (
    Bill,
    Category,
    Menu,
    MenuItem,
    Order,
    Reception,
    Reservation,
    Table,
    Waiter,
)
from .serializers import (
    BillSerializer,
    CategorySerializer,
    MenuItemSerializer,
    MenuSerializer,
    OrderSerializer,
    ReceptionSerializer,
    ReservationSerializer,
    TableSerializer,
    WaiterSerializer,
)


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.select_related("category").all()
    serializer_class = MenuSerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class WaiterViewSet(viewsets.ModelViewSet):
    queryset = Waiter.objects.all()
    serializer_class = WaiterSerializer


class ReceptionViewSet(viewsets.ModelViewSet):
    queryset = Reception.objects.all()
    serializer_class = ReceptionSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    search_fields = [
        "table__number",
        "waiter__name",
    ]


class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

    def perform_create(self, serializer):
        # Automatically create a bill when an order is created
        bill = serializer.save()
        bill.calculate_total()  # Ensure the total is calculated

    def perform_update(self, serializer):
        # Automatically update the bill when an order is updated
        bill = serializer.save()
        bill.calculate_total()  # Ensure the total is recalculated


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    @action(detail=False, methods=["get"], url_path="available-tables")
    def get_available_tables(self, request):
        capacity = request.query_params.get("capacity", None)

        if not capacity:
            return Response(
                {"error": "Capacity parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            capacity = int(capacity)
        except ValueError:
            return Response(
                {"error": "Capacity must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        available_tables = Table.objects.filter(
            status="Available", capacity__gte=capacity
        )

        if available_tables.exists():
            serializer = TableSerializer(available_tables, many=True)
            return Response(serializer.data)
        else:
            return Response(
                {
                    "message": "No open tables available for the specified capacity.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
