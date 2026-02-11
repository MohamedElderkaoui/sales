# dashboard/admin.py
from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html
from .models import GraphConfig


class SaleInline(admin.TabularInline):
    """Inline para visualizar ventas asociadas al gráfico"""
    model = GraphConfig.sales.through
    extra = 1
    verbose_name = "Venta"
    verbose_name_plural = "Ventas Asociadas"
    
    # Campos de solo lectura para mostrar info de la venta
    readonly_fields = ['get_sale_info']
    fields = ['sale', 'get_sale_info']
    
    def get_sale_info(self, obj):
        if obj.sale:
            return format_html(
                '<strong>{}</strong> - ${} ({})',
                obj.sale.customer.name,
                obj.sale.total_price,
                obj.sale.sale_date.strftime('%Y-%m-%d')
            )
        return "-"
    get_sale_info.short_description = "Detalles de la Venta"


@admin.register(GraphConfig)
class GraphConfigAdmin(admin.ModelAdmin):
    """Administrador avanzado para configuración de gráficos"""
    
    list_display = [
        'name',
        'chart_type',
        'get_sales_count',
        'get_total_revenue',
        'created_at',
        'get_chart_icon'
    ]
    
    list_filter = [
        'chart_type',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'sales__customer__name',
        'sales__product__name'
    ]
    
    filter_horizontal = ['sales']
    
    readonly_fields = [
        'created_at',
        'get_sales_count',
        'get_total_revenue',
        'get_sales_summary'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'chart_type')
        }),
        ('Datos del Gráfico', {
            'fields': ('sales',),
            'description': 'Selecciona las ventas que se incluirán en este gráfico'
        }),
        ('Estadísticas', {
            'fields': ('get_sales_count', 'get_total_revenue', 'get_sales_summary', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    
    actions = ['duplicate_graph_config', 'clear_sales']
    
    # Métodos personalizados para list_display
    
    @admin.display(description='Ventas', ordering='sales_count')
    def get_sales_count(self, obj):
        count = obj.sales.count()
        if count == 0:
            return format_html('<span style="color: red;">0 ventas</span>')
        elif count < 5:
            return format_html('<span style="color: orange;">{} ventas</span>', count)
        else:
            return format_html('<span style="color: green;">{} ventas</span>', count)
    
    @admin.display(description='Ingresos Totales', ordering='total_revenue')
    def get_total_revenue(self, obj):
        total = obj.sales.aggregate(total=Sum('total_price'))['total']
        if total:
            return format_html('<strong>${:,.2f}</strong>', total)
        return '$0.00'
    
    @admin.display(description='Tipo')
    def get_chart_icon(self, obj):
        icons = {
            'bar': '📊',
            'line': '📈',
            'pie': '🥧'
        }
        return format_html('{} {}', icons.get(obj.chart_type, '📉'), obj.get_chart_type_display())
    
    @admin.display(description='Resumen de Ventas')
    def get_sales_summary(self, obj):
        """Muestra un resumen detallado de las ventas"""
        sales = obj.sales.all()
        if not sales:
            return "No hay ventas asociadas"
        
        summary = []
        summary.append(f"<strong>Total de ventas:</strong> {sales.count()}<br>")
        
        # Agrupar por cliente
        customers = sales.values('customer__name').annotate(
            count=Count('id'),
            total=Sum('total_price')
        ).order_by('-total')[:5]
        
        if customers:
            summary.append("<strong>Top 5 Clientes:</strong><ul>")
            for customer in customers:
                summary.append(
                    f"<li>{customer['customer__name']}: "
                    f"{customer['count']} ventas - ${customer['total']:,.2f}</li>"
                )
            summary.append("</ul>")
        
        return format_html(''.join(summary))
    
    # Métodos para optimizar queries
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            sales_count=Count('sales'),
            total_revenue=Sum('sales__total_price')
        )
        return qs.prefetch_related('sales', 'sales__customer', 'sales__product')
    
    # Acciones personalizadas
    
    @admin.action(description='Duplicar configuración de gráfico')
    def duplicate_graph_config(self, request, queryset):
        """Duplica las configuraciones de gráfico seleccionadas"""
        count = 0
        for graph in queryset:
            sales = list(graph.sales.all())
            graph.pk = None
            graph.name = f"{graph.name} (Copia)"
            graph.save()
            graph.sales.set(sales)
            count += 1
        
        self.message_user(
            request,
            f"{count} configuración(es) de gráfico duplicada(s) exitosamente."
        )
    
    @admin.action(description='Limpiar ventas asociadas')
    def clear_sales(self, request, queryset):
        """Elimina todas las ventas asociadas a los gráficos seleccionados"""
        count = 0
        for graph in queryset:
            graph.sales.clear()
            count += 1
        
        self.message_user(
            request,
            f"Ventas eliminadas de {count} gráfico(s)."
        )
    
    # Personalización de formularios
    
    def save_model(self, request, obj, form, change):
        """Agrega lógica personalizada al guardar"""
        super().save_model(request, obj, form, change)
        
        # Log o notificación
        if change:
            self.message_user(
                request,
                f'Gráfico "{obj.name}" actualizado correctamente.',
                level='success'
            )
        else:
            self.message_user(
                request,
                f'Gráfico "{obj.name}" creado exitosamente.',
                level='success'
            )
