from django.db import models
from django.core.validators import MinValueValidator
from users.models import CustomUser as User
from products.models import Product
import string
import random


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.product.price * self.quantity

    @property
    def is_unavailable(self):
        return self.product.in_stock <= self.quantity

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    class Meta:
        unique_together = ("user", "product")


OrderStatus = models.TextChoices(
    "OrderStatus", "pending processing shipped delivered cancelled"
)
PaymentStatus = models.TextChoices("PaymentStatus", "pending paid failed")


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    order_number = models.CharField(
        max_length=50, unique=True, null=True, blank=True, db_index=True
    )
    status = models.CharField(
        max_length=50,
        choices=OrderStatus.choices,
        default=OrderStatus.pending,
        db_index=True,
    )
    payment_status = models.CharField(
        max_length=50, choices=PaymentStatus.choices, default=PaymentStatus.pending
    )
    shipping_address = models.ForeignKey(
        "ShippingAddress", on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number} by {self.user.username}"

    def generate_random_string(self, length):
        chars = list(string.ascii_lowercase + string.digits)
        return "".join(random.choice(chars) for _ in range(length))

    def save(self, *args, **kwargs):
        if not self.order_number:
            while True:
                self.order_number = self.generate_random_string(9)
                if not Order.objects.filter(order_number=self.order_number).exists():
                    break
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.product.name} ({self.quantity})"


class ShippingAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=255)

    def __str__(self):
        return (
            f"{self.user.username} - {self.address_line_1}, {self.city}, {self.country}"
        )
