# analytics/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Sum, Count
from .models import SalesMetric, DashboardFilter


@admin.register(SalesMetric)
class SalesMetricAdmin(admin.ModelAdmin):
    """Administrador avanzado para métricas de ventas"""
    
    list_display = [
        'get_sale_id',
        'get_customer',
        'get_product',
        'revenue',
        'profit',
        'get_profit_margin',
        'get_performance',
        'created_at'
    ]
    
    list_filter = [
        'created_at',
        'sale__product__category',
    ]
    
    search_fields = [
        'sale__customer__name',
        'sale__product__name'
    ]
    
    readonly_fields = [
        'created_at',
        'get_sale_details',
        'get_profit_margin',
        'get_roi'
    ]
    
    fieldsets = (
        ('Venta Asociada', {
            'fields': ('sale',)
        }),
        ('Métricas Financieras', {
            'fields': ('revenue', 'profit')
        }),
        ('Análisis', {
            'fields': ('get_profit_margin', 'get_roi', 'get_sale_details'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    
    actions = ['recalculate_metrics', 'export_metrics']
    
    # Métodos personalizados
    
    @admin.display(description='ID Venta', ordering='sale__id')
    def get_sale_id(self, obj):
        return format_html(
            '<a href="/admin/sales/sale/{}/change/">Venta #{}</a>',
            obj.sale.id,
            obj.sale.id
        )
    
    @admin.display(description='Cliente', ordering='sale__customer__name')
    def get_customer(self, obj):
        return obj.sale.customer.name
    
    @admin.display(description='Producto', ordering='sale__product__name')
    def get_product(self, obj):
        return obj.sale.product.name
    
    @admin.display(description='Margen (%)', ordering='profit')
    def get_profit_margin(self, obj):
        if obj.revenue > 0:
            margin = (obj.profit / obj.revenue) * 100
            
            if margin > 40:
                color = 'green'
            elif margin > 20:
                color = 'blue'
            elif margin > 0:
                color = 'orange'
            else:
                color = 'red'
            
            return format_html(
                '<strong style="color: {};">{:.1f}%</strong>',
                color,
                margin
            )
        return '0%'
    
    @admin.display(description='Rendimiento')
    def get_performance(self, obj):
        if obj.revenue > 0:
            margin = (obj.profit / obj.revenue) * 100
            
            if margin > 40:
                return format_html('<span style="color: green;">📈 Excelente</span>')
            elif margin > 20:
                return format_html('<span style="color: blue;">✓ Bueno</span>')
            elif margin > 0:
                return format_html('<span style="color: orange;">⚠️ Regular</span>')
            else:
                return format_html('<span style="color: red;">📉 Bajo</span>')
        return '-'
    
    @admin.display(description='ROI')
    def get_roi(self, obj):
        """Return on Investment"""
        if obj.revenue > 0:
            cost = obj.revenue - obj.profit
            if cost > 0:
                roi = (obj.profit / cost) * 100
                return format_html(
                    '<strong style="color: green;">{:.1f}%</strong>',
                    roi
                )
        return 'N/A'
    
    @admin.display(description='Detalles de la Venta')
    def get_sale_details(self, obj):
        sale = obj.sale
        return format_html(
            '<div style="padding: 10px; background: #f5f5f5; border-radius: 5px;">'
            '<strong>Cliente:</strong> {}<br>'
            '<strong>Producto:</strong> {}<br>'
            '<strong>Cantidad:</strong> {}<br>'
            '<strong>Precio Total:</strong> ${:,.2f}<br>'
            '<strong>Fecha:</strong> {}'
            '</div>',
            sale.customer.name,
            sale.product.name,
            sale.quantity,
            sale.total_price,
            sale.sale_date.strftime('%Y-%m-%d %H:%M')
        )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('sale__customer', 'sale__product')
    
    # Acciones personalizadas
    
    @admin.action(description='Recalcular métricas')
    def recalculate_metrics(self, request, queryset):
        """Recalcula las métricas de las ventas seleccionadas"""
        for metric in queryset:
            # Lógica de cálculo
            metric.revenue = metric.sale.total_price
            # Ejemplo: profit = 40% del revenue
            metric.profit = metric.revenue * 0.4
            metric.save()
        
        count = queryset.count()
        self.message_user(
            request,
            f'Métricas recalculadas para {count} venta(s).'
        )
    
    @admin.action(description='Exportar métricas a CSV')
    def export_metrics(self, request, queryset):
        count = queryset.count()
        self.message_user(
            request,
            f'Exportando {count} métrica(s)... (implementar exportación)'
        )


@admin.register(DashboardFilter)
class DashboardFilterAdmin(admin.ModelAdmin):
    """Administrador para filtros de dashboard"""
    
    list_display = [
        'name',
        'active',
        'get_status',
        'created_at',
        'get_age'
    ]
    
    list_filter = [
        'active',
        'created_at',
    ]
    
    search_fields = ['name']
    
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Información del Filtro', {
            'fields': ('name', 'active')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    list_editable = ['active']
    
    date_hierarchy = 'created_at'
    
    actions = ['activate_filters', 'deactivate_filters', 'duplicate_filters']
    
    # Métodos personalizados
    
    @admin.display(description='Estado', ordering='active')
    def get_status(self, obj):
        if obj.active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Activo</span>')
        else:
            return format_html('<span style="color: red;">✗ Inactivo</span>')
    
    @admin.display(description='Antigüedad')
    def get_age(self, obj):
        from django.utils import timezone
        delta = timezone.now() - obj.created_at
        days = delta.days
        
        if days == 0:
            return '🆕 Hoy'
        elif days == 1:
            return 'Ayer'
        elif days < 30:
            return f'{days} días'
        else:
            months = days // 30
            return f'{months} mes(es)'
    
    # Acciones personalizadas
    
    @admin.action(description='Activar filtros')
    def activate_filters(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(
            request,
            f'{updated} filtro(s) activado(s).'
        )
    
    @admin.action(description='Desactivar filtros')
    def deactivate_filters(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(
            request,
            f'{updated} filtro(s) desactivado(s).'
        )
    
    @admin.action(description='Duplicar filtros')
    def duplicate_filters(self, request, queryset):
        count = 0
        for filter_obj in queryset:
            filter_obj.pk = None
            filter_obj.name = f"{filter_obj.name} (Copia)"
            filter_obj.save()
            count += 1
        
        self.message_user(
            request,
            f'{count} filtro(s) duplicado(s).'
        )
