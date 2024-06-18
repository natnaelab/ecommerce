from rest_framework import serializers
from django.db import transaction
from products.serializers import ProductSerializer
from products.models import Product
from .models import CartItem, Order, ShippingAddress, OrderItem, OrderStatus


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(read_only=True, source="product")
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = (
            "id",
            "user",
            "product",
            "product_detail",
            "quantity",
            "is_unavailable",
            "total_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("user",)

    def validate(self, attrs):
        product = attrs.get("product")
        if CartItem.objects.filter(
            user=self.context["request"].user, product=product
        ).exists():
            raise serializers.ValidationError("Product already in your cart")
        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        cart_item = CartItem.objects.create(**validated_data)
        return cart_item


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = (
            "id",
            "user",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "country",
            "postal_code",
        )
        read_only_fields = ("user",)


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.CharField(source="price")

    def get_total_price(self, obj):
        return obj.price

    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "total_price")
        read_only_fields = ("id",)


class OrderSerializer(serializers.ModelSerializer):
    shipping_address = ShippingAddressSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "items",
            "shipping_address",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "user", "items", "created_at", "updated_at")

    def validate(self, attrs):
        if self.instance and attrs.get("status") not in OrderStatus.choices:
            raise serializers.ValidationError("Invalid status")

        user = self.context["request"].user
        if not CartItem.objects.filter(user=user).exists():
            raise serializers.ValidationError("You have no items in the cart.")
        if not ShippingAddress.objects.filter(user=user).exists():
            raise serializers.ValidationError("You have no shipping address.")
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        cart_items = (
            CartItem.objects.filter(user=user)
            .select_related("product")
            .prefetch_related("product__images")
        )

        order = Order.objects.create(
            shipping_address=user.shippingaddress, **validated_data
        )

        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.total_price,
                )
                for cart_item in cart_items
            ]
        )
        cart_items.delete()

        return order

    def update(self, instance, validated_data):
        instance.status = validated_data.get("status")
        instance.save()

        return super().update(instance, validated_data)
