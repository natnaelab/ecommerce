from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Product, Category


class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(method="filter_by_category")
    price = filters.RangeFilter()

    class Meta:
        model = Product
        fields = ("category", "price")

    def filter_by_category(self, queryset, name, value):
        try:
            category = Category.objects.get(id=value)
            categories = category.get_descendants(include_self=True)
            return queryset.filter(category__in=categories)
        except Category.DoesNotExist:
            return queryset.none()
