from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

# Create your models here.
# Abstract base class for shared fields
class SharedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Table model
class Table(models.Model):
    STATUS_CHOICES = [
        ("Available", "Available"),
        ("Reserved", "Reserved"),
        ("Occupied", "Occupied"),
    ]

    number = models.IntegerField(unique=True, validators=[MinValueValidator(1)])
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Available")

    def __str__(self):
        return f"Table {self.number}"


# Category model
class Category(SharedModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Menu model
class Menu(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.01)])
    category = models.ForeignKey("Category", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# MenuItem model
class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.01)])

    def __str__(self):
        return self.name


# Waiter model
class Waiter(SharedModel):
    name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(1)])  # Ensures age is positive

    def __str__(self):
        return self.name


# Reception model
class Reception(SharedModel):
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    menu_items = models.ManyToManyField(MenuItem, related_name="orders")  # Many-to-Many with MenuItem
    timestamp = models.DateTimeField(auto_now_add=True)
    waiter = models.ForeignKey("Waiter", on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.id} at Table {self.table.number}"

    def calculate_total(self):
        # Summing up the price of all menu items in this order
        return sum(item.price for item in self.menu_items.all())


class Bill(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="bill")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)

    def calculate_total(self):
        # Calculate total based on the prices of menu items in the related order
        total = sum(item.price for item in self.order.menu_items.all())
        self.total_amount = total
        # Save the updated total_amount without triggering another save loop
        super().save(update_fields=["total_amount"])

    def save(self, *args, **kwargs):
        if not self.pk:  # If this is a new Bill instance (Bill not yet saved in DB)
            super().save(*args, **kwargs)  # Save the Bill instance to create it in DB
            self.calculate_total()  # Calculate total after the Bill is created
        else:
            super().save(*args, **kwargs)  # For updates, just save normally

    def pay_bill(self):
        self.is_paid = True
        self.save(update_fields=["is_paid"])


# Signal to auto-generate Bill when an Order is created
@receiver(post_save, sender=Order)
def create_bill_for_order(sender, instance, created, **kwargs):
    if created:
        # Create a bill immediately when the order is created
        Bill.objects.create(order=instance)
    else:
        # Update the existing bill when the order is updated
        instance.bill.calculate_total()


# Reservation model
class Reservation(SharedModel):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    reservation_time = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)

    def reserve_table(self):
        self.table.status = "Reserved"
        self.table.save()
