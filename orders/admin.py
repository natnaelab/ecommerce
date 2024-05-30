from django.contrib import admin
from .models import CartItem, Order, ShippingAddress

admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(ShippingAddress)
