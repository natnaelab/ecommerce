from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from django.db import transaction
from .models import CartItem, Order, ShippingAddress
from .serializers import CartItemSerializer, OrderSerializer, ShippingAddressSerializer
from common.permissions import IsManager
import stripe


stripe.api_key = settings.STRIPE_SECRET_KEY


# CartItem View
class CartItemListCreate(generics.ListCreateAPIView):
    """
    List all cart items or create a new cart item.
    """

    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product = serializer.validated_data["product"]
        cart_item, created = self._add_or_update_cart_item(product, serializer)
        print(cart_item, created)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        print(status_code)
        return Response(CartItemSerializer(cart_item).data, status=status_code)

    def _add_or_update_cart_item(self, product, serializer):
        with transaction.atomic():
            existing_cart_item = (
                CartItem.objects.select_for_update()
                .filter(user=self.request.user, product=product)
                .first()
            )
            

            if existing_cart_item:
                existing_cart_item.quantity += 1
                existing_cart_item.save()
                return existing_cart_item, False
            else:
                cart_item = serializer.save(user=self.request.user)
                return cart_item, True


class CartItemUpdateDestroy(generics.UpdateAPIView, generics.DestroyAPIView):
    """
    Update or delete a cart item
    """

    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


# Order View
class OrderListCreate(generics.ListCreateAPIView):
    """
    List all orders or create a new order
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        print(self.request.user)
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        cart_items = CartItem.objects.filter(user=self.request.user)
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        shpping_address_data = self.request.data.pop("shipping_address")
        shipping_address, created = ShippingAddress.objects.get_or_create(
            user=self.request.user, **shpping_address_data
        )
        order = serializer.save(
            user=self.request.user,
            total_price=total_price,
            shipping_address=shipping_address,
        )
        order.items.set(cart_items)
        order.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return {"yes": "no"}
        # return super().create(request, *args, **kwargs)


class OrderStatusUpdate(generics.UpdateAPIView):
    """
    Update the status of an order
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

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


class ShippingAddressCreate(generics.CreateAPIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ShippingAddressRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

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
