from django.db import models
from django.contrib.auth import get_user_model
from django.db import transaction
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
class Table(SharedModel):
    STATUS_CHOICES = [
        ("Available", "Available"),
        ("Reserved", "Reserved"),
        ("Occupied", "Occupied"),
    ]

    number = models.IntegerField(unique=True, validators=[MinValueValidator(1)])
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
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
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    category = models.ForeignKey("Category", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# MenuItem model
class MenuItem(SharedModel):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )

    def __str__(self):
        return self.name


# Waiter model
class Waiter(SharedModel):
    name = models.CharField(max_length=100)
    age = models.IntegerField(
        validators=[MinValueValidator(1)]
    )  # Ensures age is positive

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
    menu_items = models.ManyToManyField(MenuItem, related_name="orders")
    waiter = models.ForeignKey(Waiter, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order {self.id} at Table {self.table.number}"

    def calculate_total(self):
        """Calculate the total price of all menu items in this order."""
        total = sum(item.price for item in self.menu_items.all())
        return total

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ensure Bill total is updated after all menu_items are added
        if hasattr(self, 'bill'):
            transaction.on_commit(lambda: self.bill.calculate_total())


# Bill model
class Bill(SharedModel):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="bill")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)

    def calculate_total(self):
        """Calculate the total based on the prices of menu items in the related order."""
        if self.order:
            self.total_amount = self.order.calculate_total()
            # Save the updated total_amount without triggering another save loop
            super().save(update_fields=["total_amount"])

    def save(self, *args, **kwargs):
        if not self.pk:  # This is a new Bill instance
            super().save(*args, **kwargs)  # Save to create Bill in DB
            self.calculate_total()  # Then calculate the total
        else:
            super().save(*args, **kwargs)  # For updates, save normally


# Signal to create/update the Bill whenever the Order is created or updated
@receiver(post_save, sender=Order)
def create_or_update_bill(sender, instance, created, **kwargs):
    if created:
        # Create a new Bill when an Order is created
        Bill.objects.create(order=instance)
    else:
        # Update the Bill total when the Order is updated
        if hasattr(instance, "bill"):
            # Ensure the total is recalculated after transaction is committed
            transaction.on_commit(lambda: instance.bill.calculate_total())


# Reservation model
class Reservation(SharedModel):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    reservation_time = models.DateTimeField()
    is_confirmed = models.BooleanField(default=False)

    def confirm_reservation(self):
        if not self.is_confirmed:
            self.is_confirmed = True
            self.table.status = "Reserved"
            self.table.save()
            self.save(update_fields=["is_confirmed"])

    def cancel_reservation(self):
        if self.is_confirmed:
            self.is_confirmed = False
            self.table.status = "Available"
            self.table.save()
            self.save(update_fields=["is_confirmed"])
