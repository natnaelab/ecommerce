from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Product, ProductReview, Category

admin.site.register(Product)
admin.site.register(ProductReview)


class CustomMPTTModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 10


admin.site.register(Category, CustomMPTTModelAdmin)
