from rest_framework import generics, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Product, ProductImage, ProductReview, Category
from .serializers import (
    ProductSerializer,
    ProductImageSerializer,
    ProductReviewSerializer,
    CategorySerializer,
)

from common.permissions import IsManager
from .permissions import IsManagerAndProductOwner, IsManagerOrReadOnly
from .filters import ProductFilter
from .paginations import ProductPagination


class ProductQuerySetMixin:
    def get_queryset(self):
        return (
            Product.objects.select_related("added_by", "category")
            .prefetch_related("images")
            .order_by("-created_at")
        )


class ProductListCreateView(ProductQuerySetMixin, generics.ListCreateAPIView):
    """
    List all products or create a new product.

    GET: Returns a list of all products, with optional filtering, ordering, and search capabilities.
    POST: Creates a new product. Only accessible by managers
    """

    serializer_class = ProductSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = ProductFilter
    ordering_fields = ["price"]
    search_fields = ["name", "description"]
    pagination_class = ProductPagination
    permission_classes = [IsManagerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class ProductRetrieveUpdateDestroyView(
    ProductQuerySetMixin, generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update or delete a product.

    GET: Retrieves a product. Accessible by any user.
    PUT/PATCH: Updates a product. Only accessible by manager who created the product.
    DELETE: Deletes a product. Only accessible by manager who created the product.
    """

    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return (permissions.AllowAny(),)
        return (IsManagerAndProductOwner(),)


class ProductImageUpdateDestroyView(generics.UpdateAPIView, generics.DestroyAPIView):
    """
    Update or delete product image.

    PUT/PATCH: Updates a product image. Only accessible by the manager who created the product.
    DELETE: Deletes a product image. Only accessible by the manager who created the product.
    """

    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product__added_by=self.request.user)

    def get_permissions(self):
        return (IsManager(),)


class ProductReviewListCreateView(generics.ListCreateAPIView):
    """
    List all reviews for specific product or create a new review for that product

    GET: Returns a list of reviews for the specified product.
    POST: Creates a new review for the specified product. Only accessible by authenticated users.
    """

    serializer_class = ProductReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_product_or_404(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get_queryset(self):
        return ProductReview.objects.filter(
            product__pk=self.kwargs["pk"]
        ).select_related("user")

    def perform_create(self, serializer):
        product = self.get_product_or_404(self.kwargs["pk"])
        serializer.save(user=self.request.user, product=product)


class ProductReviewUpdateDestroyView(generics.UpdateAPIView, generics.DestroyAPIView):
    """
    Update or delete a review on a specific product.

    PUT/PATCH: Updates a review. Only accessible by the review creator.
    DELETE: Deletes a review. Only accessible by the review creator.
    """

    serializer_class = ProductReviewSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return ProductReview.objects.filter(
            product__pk=self.kwargs["pk"], user=self.request.user
        ).select_related("user")


class CategoriesListView(generics.ListAPIView):
    """
    List all categories and subcategories
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return Category.objects.prefetch_related("children").filter(parent=None)


class CategoryRetrieveView(generics.RetrieveAPIView):
    """
    Retrieve a specific category and its subcategories
    """

    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        pk = self.kwargs["pk"]
        return Category.objects.filter(pk=pk)
