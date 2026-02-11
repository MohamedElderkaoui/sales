# analytics/views.py
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate, TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_filters import rest_framework as filters
from datetime import datetime, timedelta

from sales.models import Sale, Product, Customer
from .serializers import (
    SaleSerializer, KPISerializer, SalesByPeriodSerializer,
    SalesByCategorySerializer, TopCustomerSerializer, ProductDistributionSerializer
)


class SaleFilter(filters.FilterSet):
    """Filtros avanzados para ventas"""
    date_from = filters.DateFilter(field_name='sale_date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='sale_date', lookup_expr='lte')
    category = filters.CharFilter(field_name='product__category', lookup_expr='icontains')
    product = filters.NumberFilter(field_name='product_id')
    customer = filters.NumberFilter(field_name='customer_id')
    search = filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            customer__name__icontains=value
        ) | queryset.filter(
            product__name__icontains=value
        )

    class Meta:
        model = Sale
        fields = ['date_from', 'date_to', 'category', 'product', 'customer']


class KPIView(APIView):
    """Métricas KPI generales"""
    
    def get(self, request):
        queryset = Sale.objects.all()
        filterset = SaleFilter(request.query_params, queryset=queryset)
        qs = filterset.qs
        
        aggregates = qs.aggregate(
            total_sales=Sum('total_price'),
            total_orders=Count('id'),
            average_order=Avg('total_price')
        )
        
        total_customers = qs.values('customer').distinct().count()
        
        data = {
            'total_sales': aggregates['total_sales'] or 0,
            'total_orders': aggregates['total_orders'] or 0,
            'average_order': aggregates['average_order'] or 0,
            'total_customers': total_customers
        }
        
        serializer = KPISerializer(data)
        return Response(serializer.data)


class SalesByPeriodView(APIView):
    """Ventas agrupadas por día o mes"""
    
    def get(self, request):
        queryset = Sale.objects.all()
        filterset = SaleFilter(request.query_params, queryset=queryset)
        qs = filterset.qs
        
        group_by = request.query_params.get('group_by', 'day')
        
        if group_by == 'month':
            qs = qs.annotate(period=TruncMonth('sale_date'))
        else:
            qs = qs.annotate(period=TruncDate('sale_date'))
        
        data = qs.values('period').annotate(
            total=Sum('total_price'),
            count=Count('id')
        ).order_by('period')
        
        result = [
            {
                'period': item['period'].strftime('%Y-%m-%d') if group_by == 'day' else item['period'].strftime('%Y-%m'),
                'total': item['total'],
                'count': item['count']
            }
            for item in data if item['period']
        ]
        
        serializer = SalesByPeriodSerializer(result, many=True)
        return Response(serializer.data)


class SalesByCategoryView(APIView):
    """Ventas agrupadas por categoría de producto"""
    
    def get(self, request):
        queryset = Sale.objects.all()
        filterset = SaleFilter(request.query_params, queryset=queryset)
        qs = filterset.qs
        
        data = qs.values('product__category').annotate(
            total=Sum('total_price'),
            count=Count('id')
        ).order_by('-total')
        
        result = [
            {
                'category': item['product__category'] or 'Sin categoría',
                'total': item['total'],
                'count': item['count']
            }
            for item in data
        ]
        
        serializer = SalesByCategorySerializer(result, many=True)
        return Response(serializer.data)


class TopCustomersView(APIView):
    """Top clientes por volumen de compra"""
    
    def get(self, request):
        queryset = Sale.objects.all()
        filterset = SaleFilter(request.query_params, queryset=queryset)
        qs = filterset.qs
        
        limit = int(request.query_params.get('limit', 10))
        
        data = qs.values('customer_id', 'customer__name').annotate(
            total_spent=Sum('total_price'),
            order_count=Count('id')
        ).order_by('-total_spent')[:limit]
        
        result = [
            {
                'customer_id': item['customer_id'],
                'customer_name': item['customer__name'],
                'total_spent': item['total_spent'],
                'order_count': item['order_count']
            }
            for item in data
        ]
        
        serializer = TopCustomerSerializer(result, many=True)
        return Response(serializer.data)


class ProductDistributionView(APIView):
    """Distribución de productos vendidos"""
    
    def get(self, request):
        queryset = Sale.objects.all()
        filterset = SaleFilter(request.query_params, queryset=queryset)
        qs = filterset.qs
        
        limit = int(request.query_params.get('limit', 10))
        
        data = qs.values('product__name').annotate(
            quantity_sold=Sum('quantity'),
            revenue=Sum('total_price')
        ).order_by('-revenue')[:limit]
        
        result = [
            {
                'product_name': item['product__name'],
                'quantity_sold': item['quantity_sold'],
                'revenue': item['revenue']
            }
            for item in data
        ]
        
        serializer = ProductDistributionSerializer(result, many=True)
        return Response(serializer.data)


class SalesListView(APIView):
    """Lista de ventas con filtros y búsqueda"""
    
    def get(self, request):
        queryset = Sale.objects.select_related('customer', 'product').all()
        filterset = SaleFilter(request.query_params, queryset=queryset)
        qs = filterset.qs.order_by('-sale_date')
        
        # Paginación simple
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 25))
        start = (page - 1) * per_page
        end = start + per_page
        
        total = qs.count()
        sales = qs[start:end]
        
        serializer = SaleSerializer(sales, many=True)
        return Response({
            'data': serializer.data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
