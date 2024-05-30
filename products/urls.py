from django.urls import path, include
from django.conf import settings
from .views import (
    ProductListCreateView,
    ProductRetrieveUpdateDestroy,
    ProductImageList,
    ProductImageUpdateDestroy,
    ProductReviewListCreateView,
    ProductReviewUpdateDestroyView,
    CategoriesListView,
    CategoryRetrieveView,
)


urlpatterns = [
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path(
        "products/<int:pk>/",
        ProductRetrieveUpdateDestroy.as_view(),
        name="product-retrieve-update-destroy",
    ),
    path(
        "products/<int:pk>/images/",
        ProductImageList.as_view(),
        name="product-image-list",
    ),
    path(
        "products/images/<int:pk>/",
        ProductImageUpdateDestroy.as_view(),
        name="product-image-update-destroy",
    ),
    path(
        "products/<int:pk>/reviews/",
        ProductReviewListCreateView.as_view(),
        name="product-review-list-create",
    ),
    path(
        "products/reviews/<int:pk>/",
        ProductReviewUpdateDestroyView.as_view(),
        name="product-review-update-destroy",
    ),
    path("categories/", CategoriesListView.as_view(), name="categories-list"),
    path(
        "categories/<int:pk>/", CategoryRetrieveView.as_view(), name="category-retrieve"
    ),
]
