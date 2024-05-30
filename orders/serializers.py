from rest_framework import serializers
from .models import CartItem, Order, ShippingAddress


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("id", "user", "product", "quantity", "created_at", "updated_at")
        read_only_fields = ("user",)

    def create(self, validated_data):
        user = self.context["request"].user
        return CartItem.objects.create(user=user, **validated_data)


class OrderSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "items",
            "total_price",
            "status",
            "created_at",
            "updated_at",
        )

    def validate_status(self, value):
        if value not in ("Pending", "Processing", "Shipped", "Delivered", "Cancelled"):
            raise serializers.ValidationError("Invalid status")

        return value


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = "__all__"
