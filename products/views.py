from rest_framework import generics, filters, permissions
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Product, ProductImage, ProductReview, Category
from .serializers import (
    ProductSerializer,
    ProductImageSerializer,
    ProductReviewSerializer,
    CategorySerializer,
)

from common.permissions import IsManager
from .permissions import IsManagerAndProductOwner


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ProductListCreateView(generics.ListCreateAPIView):
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
    filterset_fields = ["price", "stock", "category"]
    ordering_fields = ["price", "stock"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        qs = Product.objects.prefetch_related("images").select_related("category")
        if self.request.method == "GET":
            return qs
        return qs.filter(added_by=self.request.user)

    def get_permissions(self):
        if self.request.method == "GET":
            return (permissions.AllowAny(),)
        return (IsManager(),)

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class ProductRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a product.

    GET: Retrieves a product. Accessible by any user.
    PUT/PATCH: Updates a product. Only accessible by manager who created the product.
    DELETE: Deletes a product. Only accessible by manager who created the product.
    """

    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.prefetch_related("images")
        if self.request.method == "GET":
            return qs
        return qs.filter(added_by=self.request.user)

    def get_permissions(self):
        if self.request.method == "GET":
            return (permissions.AllowAny(),)
        return (IsManagerAndProductOwner(),)


class ProductImageList(generics.ListAPIView):
    """
    List all product images for a given product.

    GET:
    Returns a list of images associated with the given product ID.
    """

    serializer_class = ProductImageSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        product = get_object_or_404(Product, pk=self.kwargs["pk"])
        return product.images.all()


class ProductImageUpdateDestroy(generics.UpdateAPIView, generics.DestroyAPIView):
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

    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_product_or_404(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get_queryset(self):
        product = self.get_product_or_404(self.kwargs["pk"])
        return ProductReview.objects.filter(product=product)

    def perform_create(self, serializer):
        product = self.get_product_or_404(self.kwargs["pk"])
        serializer.save(user=self.request.user, product=product)


class ProductReviewUpdateDestroyView(generics.UpdateAPIView, generics.DestroyAPIView):
    """
    Update or delete a review on a specific product.

    PUT/PATCH: Updates a review. Only accessible by the review creator.
    DELETE: Deletes a review. Only accessible by the review creator.
    """

    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return ProductReview.objects.filter(user=self.request.user)


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
