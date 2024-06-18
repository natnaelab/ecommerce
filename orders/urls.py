from django.urls import path
from .views import (
    CartItemListCreate,
    CartItemUpdateDestroy,
    OrderListCreate,
    OrderStatusUpdate,
    ShippingAddressCreate,
    ShippingAddressRetrieve,
    ShippingAddressUpdateDestroy,
    CreateStripeCheckoutSession,
    StripeWebhook,
)


urlpatterns = [
    path("cart/", CartItemListCreate.as_view(), name="cart-item-list-create"),
    path("cart/<int:pk>/", CartItemUpdateDestroy.as_view(), name="cart-item-detail"),
    path("orders/", OrderListCreate.as_view(), name="order-create"),
    path("orders/<int:pk>/", OrderStatusUpdate.as_view(), name="order-status-update"),
    path(
        "shipping-address/",
        ShippingAddressCreate.as_view(),
        name="shipping-address-create",
    ),
    path(
        "shipping-address/user/",
        ShippingAddressRetrieve.as_view(),
        name="shipping-address-retrieve",
    ),
    path(
        "shipping-address/<int:pk>/",
        ShippingAddressUpdateDestroy.as_view(),
        name="shipping-address-create",
    ),
    # stripe
    path(
        "stripe-create-checkout-session/",
        CreateStripeCheckoutSession.as_view(),
        name="stripe-create-checkout-session",
    ),
    path(
        "stripe-webhook/",
        StripeWebhook.as_view(),
        name="stripe-webhook",
    ),
]
