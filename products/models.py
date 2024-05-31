from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    MinValueValidator,
)
from mptt.models import MPTTModel, TreeForeignKey
from users.models import CustomUser as User
from .utils import unique_slugify
from decimal import Decimal


class Product(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(validators=[MaxLengthValidator(2000)])
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal(1.00))]
    )
    in_stock = models.PositiveIntegerField()
    category = models.ForeignKey(
        "Category", related_name="products", on_delete=models.SET_NULL, null=True
    )

    def __str__(self) -> str:
        return self.name


@receiver(pre_save, sender=Product)
def set_product_slug(sender, instance, *args, **kwargs):
    if instance.pk is None:
        unique_slugify(instance)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.product.name

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(
                is_primary=False
            )
        super().save(*args, **kwargs)


class Category(MPTTModel):
    parent = TreeForeignKey(
        "self", blank=True, null=True, related_name="children", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, db_index=True)

    class Meta:
        verbose_name_plural = "Categories"

    class MPTTMeta:
        order_insertion_by = ["name"]

    def save(self, *args, **kwargs):
        unique_slugify(self)
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


@receiver(pre_save, sender=Category)
def set_category_slug(sender, instance, *args, **kwargs):
    if instance.pk is None:
        unique_slugify(instance)


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    is_verified = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}* - {self.comment}"
