from django.urls import path
from .views import (
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
    ProductImageUpdateDestroyView,
    ProductReviewListCreateView,
    ProductReviewUpdateDestroyView,
    CategoriesListView,
    CategoryRetrieveView,
)


urlpatterns = [
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path(
        "products/<int:pk>/",
        ProductRetrieveUpdateDestroyView.as_view(),
        name="product-retrieve-update-destroy",
    ),
    path(
        "products/images/<int:pk>/",
        ProductImageUpdateDestroyView.as_view(),
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
