from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from common.permissions import IsManager
from .models import CartItem, Order, ShippingAddress
from .serializers import CartItemSerializer, OrderSerializer, ShippingAddressSerializer
import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY


class CartItemListCreate(generics.ListCreateAPIView):
    """
    List all cart items or create a new cart item.
    """

    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ["price"]

    def get_queryset(self):
        return (
            CartItem.objects.filter(user=self.request.user)
            .select_related("product")
            .prefetch_related("product__images")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemUpdateDestroy(generics.UpdateAPIView, generics.DestroyAPIView):
    """
    Update or delete a cart item
    """

    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related("product")


class OrderListCreate(generics.ListCreateAPIView):
    """
    Create a new order
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("shipping_address")
            .prefetch_related("items__product__images")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderStatusUpdate(generics.UpdateAPIView):
    """
    Update the status of an order
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsManager]

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        status = request.data.get("status")

        if status:
            order.status = status
            order.save()
            return Response({"status": "success", "data": OrderSerializer(order).data})
        else:
            return Response(
                {"status": "error", "message": "Status is required."}, status=400
            )


class OrderItemRetrieve(generics.RetrieveAPIView):
    """
    Retrieve an order item
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .select_related("shipping_address")
            .prefetch_related("items__product__images")
        )


class ShippingAddressCreate(generics.CreateAPIView):
    """
    Create or update shipping address
    """

    serializer_class = ShippingAddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        try:
            shipping_address = ShippingAddress.objects.get(user=self.request.user)
            serializer.update(shipping_address, self.request.data)
        except ShippingAddress.DoesNotExist:
            serializer.save(user=self.request.user)


class ShippingAddressRetrieve(APIView):
    """
    Retrieve logged in user's shipping address
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            shipping_address = ShippingAddress.objects.get(user=self.request.user)
            serializer = ShippingAddressSerializer(shipping_address)
            return Response(serializer.data)
        except ShippingAddress.DoesNotExist:
            return Response({"error": "Shipping address not found"}, status=404)


class ShippingAddressUpdateDestroy(generics.UpdateAPIView, generics.DestroyAPIView):
    """
    Update or delete shipping address
    """

    serializer_class = ShippingAddressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)


class CreateStripeCheckoutSession(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            line_items = [
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": item.product.name,
                        },
                        "unit_amount": int(item.product.price * 100),
                    },
                    "quantity": item.quantity,
                }
                for item in order.items.all()
            ]
            session = stripe.checkout.Session.create(
                payment_method_types=["card", "paypal"],
                line_items=line_items,
                mode="payment",
                success_url="https://cb20-104-28-252-16.ngrok-free.app/success/",
                cancel_url="https://cb20-104-28-252-16.ngrok-free.app/cancel/",
                metadata={"order_id", order.id},
            )
            return Response({"id": session.id})
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class StripeWebhook(APIView):
    def post(self, request, *args, **kwargs):
        payload = request.data
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return Response(status=400)
        except stripe.error.SignatureVerificationError as e:
            return Response(status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            order_number = session["metadata"]["order_number"]
            order = Order.objects.get(order_number=order_number)
            order.payment_status = "paid"
            order.status = "processing"
            order.save()
        elif event["type"] == "checkout.session.expired":
            session = event["data"]["object"]
            order_number = session["metadata"]["order_number"]
            order = Order.objects.get(order_number=order_number)
            order.payment_status = "failed"
            order.status = "cancelled"
            order.save()

        return Response(status=200)
