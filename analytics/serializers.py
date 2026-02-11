# analytics/serializers.py
from rest_framework import serializers
from sales.models import Sale, Product, Customer


class SaleSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_category = serializers.CharField(source='product.category', read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'customer', 'customer_name', 'product', 'product_name',
            'product_category', 'quantity', 'total_price', 'sale_date'
        ]


class KPISerializer(serializers.Serializer):
    total_sales = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_orders = serializers.IntegerField()
    average_order = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_customers = serializers.IntegerField()


class SalesByPeriodSerializer(serializers.Serializer):
    period = serializers.CharField()
    total = serializers.DecimalField(max_digits=14, decimal_places=2)
    count = serializers.IntegerField()


class SalesByCategorySerializer(serializers.Serializer):
    category = serializers.CharField()
    total = serializers.DecimalField(max_digits=14, decimal_places=2)
    count = serializers.IntegerField()


class TopCustomerSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    customer_name = serializers.CharField()
    total_spent = serializers.DecimalField(max_digits=14, decimal_places=2)
    order_count = serializers.IntegerField()


class ProductDistributionSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    quantity_sold = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=14, decimal_places=2)
