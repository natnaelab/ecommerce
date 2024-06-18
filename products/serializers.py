from rest_framework import serializers
from .models import Product, ProductImage, ProductReview, Category
from users.serializers import UserSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "is_primary")
        read_only_fields = ("id", "image")


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    preview_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "added_by",
            "name",
            "slug",
            "description",
            "price",
            "in_stock",
            "category",
            "images",
            "preview_images",
        )
        read_only_fields = ("id", "added_by", "slug")

    def validate_price(self, price):
        if price <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        if price > 99_999_999_999:
            raise serializers.ValidationError("Price must be less than 99,999,999,999.")
        return price

    def create(self, validated_data):
        images = validated_data.pop("preview_images", [])
        product = Product.objects.create(**validated_data)

        for image in images:
            ProductImage.objects.create(product=product, image=image)
        return product

    def update(self, instance, validated_data):
        images = validated_data.pop("preview_images", [])
        for image in images:
            ProductImage.objects.create(product=instance, image=image)

        if "in_stock" in validated_data:
            instance.in_stock = validated_data["in_stock"]
            instance.save()
            instance.refresh_from_db()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["images"] = ProductImageSerializer(
            instance.images.all(), many=True
        ).data
        return representation


class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProductReview
        fields = (
            "id",
            "user",
            "product",
            "rating",
            "comment",
            "is_verified",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "user",
            "product",
            "created_at",
            "updated_at",
        )


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "subcategories")

    def get_subcategories(self, obj):
        return SubcategorySerializer(obj.children.all(), many=True).data


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")
