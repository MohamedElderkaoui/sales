# analytics/views.py
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate, TruncMonth
from django_filters import rest_framework as filters
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)

from sales.models import Customer, Product, Sale
from .serializers import (
    KPISerializer,
    ProductDistributionSerializer,
    SaleSerializer,
    SalesByCategorySerializer,
    SalesByPeriodSerializer,
    TopCustomerSerializer,
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

    @extend_schema(
        summary="KPIs de ventas",
        description=(
            "Devuelve métricas agregadas de ventas (importe total, nº pedidos, "
            "ticket medio y número de clientes únicos).\n\n"
            "Permite filtrar por rango de fechas, categoría, producto, cliente y búsqueda "
            "por nombre de cliente o producto."
        ),
        parameters=[
            OpenApiParameter("date_from", OpenApiTypes.DATE, description="Fecha mínima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("date_to", OpenApiTypes.DATE, description="Fecha máxima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("category", OpenApiTypes.STR, description="Filtro por categoría de producto (icontains)"),
            OpenApiParameter("product", OpenApiTypes.INT, description="ID del producto"),
            OpenApiParameter("customer", OpenApiTypes.INT, description="ID del cliente"),
            OpenApiParameter(
                "search",
                OpenApiTypes.STR,
                description="Búsqueda por nombre de cliente o producto (icontains)",
            ),
        ],
        responses={200: KPISerializer},
    )
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

    @extend_schema(
        summary="Ventas por periodo",
        description=(
            "Devuelve ventas agregadas por periodo (día o mes), con importe total y nº de pedidos.\n\n"
            "Se puede controlar la granularidad con el parámetro `group_by`.\n"
            "Admite los mismos filtros que el resto de endpoints de ventas."
        ),
        parameters=[
            OpenApiParameter("group_by", OpenApiTypes.STR, enum=["day", "month"], description="Agrupar por día o mes"),
            OpenApiParameter("date_from", OpenApiTypes.DATE, description="Fecha mínima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("date_to", OpenApiTypes.DATE, description="Fecha máxima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("category", OpenApiTypes.STR, description="Filtro por categoría de producto (icontains)"),
            OpenApiParameter("product", OpenApiTypes.INT, description="ID del producto"),
            OpenApiParameter("customer", OpenApiTypes.INT, description="ID del cliente"),
        ],
        responses={200: SalesByPeriodSerializer(many=True)},
    )
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

    @extend_schema(
        summary="Ventas por categoría",
        description=(
            "Devuelve ventas agregadas por categoría de producto, incluyendo importe total "
            "y número de pedidos por categoría."
        ),
        parameters=[
            OpenApiParameter("date_from", OpenApiTypes.DATE, description="Fecha mínima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("date_to", OpenApiTypes.DATE, description="Fecha máxima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("category", OpenApiTypes.STR, description="Filtro por categoría de producto (icontains)"),
            OpenApiParameter("product", OpenApiTypes.INT, description="ID del producto"),
            OpenApiParameter("customer", OpenApiTypes.INT, description="ID del cliente"),
        ],
        responses={200: SalesByCategorySerializer(many=True)},
    )
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

    @extend_schema(
        summary="Top clientes",
        description=(
            "Devuelve el ranking de clientes por volumen de compra (importe total y nº de pedidos)."
        ),
        parameters=[
            OpenApiParameter(
                "limit",
                OpenApiTypes.INT,
                description="Número máximo de clientes a devolver",
                default=10,
            ),
            OpenApiParameter("date_from", OpenApiTypes.DATE, description="Fecha mínima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("date_to", OpenApiTypes.DATE, description="Fecha máxima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("category", OpenApiTypes.STR, description="Filtro por categoría de producto (icontains)"),
            OpenApiParameter("product", OpenApiTypes.INT, description="ID del producto"),
            OpenApiParameter("customer", OpenApiTypes.INT, description="ID del cliente"),
        ],
        responses={200: TopCustomerSerializer(many=True)},
    )
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

    @extend_schema(
        summary="Distribución de productos vendidos",
        description=(
            "Devuelve la distribución de productos vendidos, incluyendo cantidad total vendida "
            "y facturación por producto."
        ),
        parameters=[
            OpenApiParameter(
                "limit",
                OpenApiTypes.INT,
                description="Número máximo de productos a devolver",
                default=10,
            ),
            OpenApiParameter("date_from", OpenApiTypes.DATE, description="Fecha mínima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("date_to", OpenApiTypes.DATE, description="Fecha máxima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("category", OpenApiTypes.STR, description="Filtro por categoría de producto (icontains)"),
            OpenApiParameter("product", OpenApiTypes.INT, description="ID del producto"),
            OpenApiParameter("customer", OpenApiTypes.INT, description="ID del cliente"),
        ],
        responses={200: ProductDistributionSerializer(many=True)},
    )
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

    @extend_schema(
        summary="Listado detallado de ventas",
        description=(
            "Devuelve un listado paginado de ventas con información de cliente y producto.\n\n"
            "Admite filtros avanzados (rango de fechas, categoría, producto, cliente y búsqueda "
            "por nombre) y paginación mediante `page` y `per_page`."
        ),
        parameters=[
            OpenApiParameter("page", OpenApiTypes.INT, description="Número de página (1-based)", default=1),
            OpenApiParameter(
                "per_page",
                OpenApiTypes.INT,
                description="Registros por página",
                default=25,
            ),
            OpenApiParameter("date_from", OpenApiTypes.DATE, description="Fecha mínima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("date_to", OpenApiTypes.DATE, description="Fecha máxima de la venta (YYYY-MM-DD)"),
            OpenApiParameter("category", OpenApiTypes.STR, description="Filtro por categoría de producto (icontains)"),
            OpenApiParameter("product", OpenApiTypes.INT, description="ID del producto"),
            OpenApiParameter("customer", OpenApiTypes.INT, description="ID del cliente"),
            OpenApiParameter(
                "search",
                OpenApiTypes.STR,
                description="Búsqueda por nombre de cliente o producto (icontains)",
            ),
        ],
        responses={
            200: inline_serializer(
                name="SalesListResponse",
                fields={
                    "data": SaleSerializer(many=True),
                    "total": serializers.IntegerField(),
                    "page": serializers.IntegerField(),
                    "per_page": serializers.IntegerField(),
                    "total_pages": serializers.IntegerField(),
                },
            )
        },
    )
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
