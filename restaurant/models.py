from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()
# Assuming User is the model name for Django's built-in User model


# Create your models here.
# Abstract base class for shared fields
class SharedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Table model
class Table(SharedModel):
    STATUS_CHOICES = [
        ("Available", "Available"),
        ("Reserved", "Reserved"),
        ("Occupied", "Occupied"),
    ]

    number = models.IntegerField(
        unique=True,
        validators=[MinValueValidator(1)],  # Ensures the table number is positive
    )
    capacity = models.IntegerField(
        validators=[MinValueValidator(1)]  # Ensures the capacity is positive
    )
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="Available"
    )

    def __str__(self):
        return f"Table {self.number}"


# Category model
class Category(SharedModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Menu model
class Menu(SharedModel):
    name = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],  # Ensures the price is positive
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Waiter model
class Waiter(SharedModel):
    name = models.CharField(max_length=100)
    age = models.IntegerField(
        validators=[MinValueValidator(1)]  # Ensures age is positive
    )

    def __str__(self):
        return self.name


# Reception model
class Reception(SharedModel):
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


# Order model
class Order(SharedModel):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    menu_items = models.ManyToManyField("Menu")
    waiter = models.ForeignKey("Waiter", on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.id} at Table {self.table.number}"


# Bill model
class Bill(SharedModel):
    order = models.OneToOneField("Order", on_delete=models.CASCADE)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],  # Ensures the total amount is positive
    )
    is_paid = models.BooleanField(default=False)

    def pay_bill(self):
        self.is_paid = True
        self.save()
        if not Reservation.objects.filter(
            table=self.order.table, is_confirmed=True
        ).exists():
            self.order.table.status = "Available"
            self.order.table.save()


# Reservation model
class Reservation(SharedModel):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    reservation_time = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)

    def reserve_table(self):
        self.table.status = "Reserved"
        self.table.save()
