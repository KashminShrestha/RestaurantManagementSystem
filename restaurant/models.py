from django.db import models


# Create your models here.
class Table(models.Model):
    number = models.IntegerField(unique=True)
    capacity = models.IntegerField()
    status = models.CharField(max_length=50)  # e.g., Available, Occupied

    def __str__(self):
        return f"Table {self.number}"


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Waiter(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()

    def __str__(self):
        return self.name


class Reception(models.Model):
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    menu_items = models.ManyToManyField(Menu)
    waiter = models.ForeignKey(Waiter, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} at Table {self.table.number}"
