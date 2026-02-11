# sales/admin.py
from django.contrib import admin
from django.db.models import Sum, Count, Avg
from django.utils.html import format_html
from django.utils import timezone
from .models import Customer, Product, Sale


class SaleInline(admin.TabularInline):
    """Inline para ventas en Customer y Product"""
    model = Sale
    extra = 0
    readonly_fields = ['total_price', 'sale_date']
    fields = ['product', 'customer', 'quantity', 'total_price', 'sale_date']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Administrador avanzado para clientes"""
    
    list_display = [
        'name',
        'email',
        'phone',
        'get_sales_count',
        'get_total_spent',
        'get_status',
        'created_at'
    ]
    
    list_filter = [
        'created_at',
        ('sales', admin.EmptyFieldListFilter),
    ]
    
    search_fields = ['name', 'email', 'phone']
    
    readonly_fields = [
        'created_at',
        'get_sales_count',
        'get_total_spent',
        'get_avg_purchase',
        'get_sales_list'
    ]
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Estadísticas de Ventas', {
            'fields': ('get_sales_count', 'get_total_spent', 'get_avg_purchase'),
            'classes': ('collapse',)
        }),
        ('Historial', {
            'fields': ('created_at', 'get_sales_list'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [SaleInline]
    
    date_hierarchy = 'created_at'
    
    actions = ['export_customer_data', 'mark_as_vip']
    
    # Métodos personalizados
    
    @admin.display(description='Ventas', ordering='sales_count')
    def get_sales_count(self, obj):
        count = obj.sales.count()
        if count == 0:
            return format_html('<span style="color: gray;">Sin ventas</span>')
        return format_html('<strong>{}</strong> ventas', count)
    
    @admin.display(description='Total Gastado', ordering='total_spent')
    def get_total_spent(self, obj):
        total = obj.sales.aggregate(total=Sum('total_price'))['total'] or 0
        if total > 10000:
            color = 'green'
        elif total > 5000:
            color = 'blue'
        else:
            color = 'orange'
        return format_html('<span style="color: {}; font-weight: bold;">${:,.2f}</span>', color, total)
    
    @admin.display(description='Promedio por Compra')
    def get_avg_purchase(self, obj):
        avg = obj.sales.aggregate(avg=Avg('total_price'))['avg'] or 0
        return f'${avg:,.2f}'
    
    @admin.display(description='Estado')
    def get_status(self, obj):
        count = obj.sales.count()
        if count == 0:
            return format_html('<span style="color: red;">⚠️ Sin actividad</span>')
        elif count >= 10:
            return format_html('<span style="color: gold;">⭐ VIP</span>')
        elif count >= 5:
            return format_html('<span style="color: green;">✓ Activo</span>')
        else:
            return format_html('<span style="color: blue;">👤 Regular</span>')
    
    @admin.display(description='Historial de Compras')
    def get_sales_list(self, obj):
        sales = obj.sales.order_by('-sale_date')[:10]
        if not sales:
            return "Sin compras"
        
        html = ['<ul style="margin: 0;">']
        for sale in sales:
            html.append(
                f'<li><strong>{sale.product.name}</strong> '
                f'x{sale.quantity} - ${sale.total_price:,.2f} '
                f'<em>({sale.sale_date.strftime("%Y-%m-%d")})</em></li>'
            )
        html.append('</ul>')
        return format_html(''.join(html))
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            sales_count=Count('sales'),
            total_spent=Sum('sales__total_price')
        )
        return qs.prefetch_related('sales__product')
    
    # Acciones
    
    @admin.action(description='Exportar datos de clientes')
    def export_customer_data(self, request, queryset):
        count = queryset.count()
        self.message_user(
            request,
            f'Exportando datos de {count} cliente(s)... (implementar lógica de exportación)'
        )
    
    @admin.action(description='Marcar como VIP')
    def mark_as_vip(self, request, queryset):
        # Aquí podrías agregar un campo is_vip al modelo
        count = queryset.count()
        self.message_user(
            request,
            f'{count} cliente(s) marcado(s) como VIP.'
        )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Administrador avanzado para productos"""
    
    list_display = [
        'name',
        'price',
        'category',
        'get_stock_status',
        'get_sales_count',
        'get_revenue',
        'get_popularity'
    ]
    
    list_filter = [
        'category',
        ('sale', admin.EmptyFieldListFilter),
    ]
    
    search_fields = ['name', 'category']
    
    readonly_fields = [
        'get_sales_count',
        'get_revenue',
        'get_avg_quantity',
        'get_top_customers'
    ]
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('name', 'price', 'category', 'in_stock')
        }),
        ('Estadísticas de Ventas', {
            'fields': ('get_sales_count', 'get_revenue', 'get_avg_quantity'),
            'classes': ('collapse',)
        }),
        ('Análisis', {
            'fields': ('get_top_customers',),
            'classes': ('collapse',)
        }),
    )
    
    list_editable = ['price', 'in_stock']
    
    actions = ['restock_products', 'apply_discount', 'mark_out_of_stock']
    
    # Métodos personalizados
    
    @admin.display(description='Stock', ordering='in_stock')
    def get_stock_status(self, obj):
        if obj.in_stock == 0:
            return format_html('<span style="color: red; font-weight: bold;">🔴 Agotado</span>')
        elif obj.in_stock < 10:
            return format_html('<span style="color: orange;">⚠️ Bajo ({} unidades)</span>', obj.in_stock)
        else:
            return format_html('<span style="color: green;">✓ {} disponibles</span>', obj.in_stock)
    
    @admin.display(description='Ventas', ordering='sales_count')
    def get_sales_count(self, obj):
        count = obj.sale_set.count()
        return format_html('<strong>{}</strong> ventas', count)
    
    @admin.display(description='Ingresos', ordering='revenue')
    def get_revenue(self, obj):
        total = obj.sale_set.aggregate(total=Sum('total_price'))['total'] or 0
        return format_html('<strong style="color: green;">${:,.2f}</strong>', total)
    
    @admin.display(description='Popularidad')
    def get_popularity(self, obj):
        count = obj.sale_set.count()
        if count == 0:
            return '⚪'
        elif count < 5:
            return '🔵'
        elif count < 10:
            return '🟢'
        elif count < 20:
            return '🟡'
        else:
            return '🔥'
    
    @admin.display(description='Cantidad Promedio')
    def get_avg_quantity(self, obj):
        avg = obj.sale_set.aggregate(avg=Avg('quantity'))['avg'] or 0
        return f'{avg:.1f} unidades'
    
    @admin.display(description='Top Clientes')
    def get_top_customers(self, obj):
        sales = obj.sale_set.select_related('customer').values(
            'customer__name'
        ).annotate(
            total=Sum('total_price'),
            count=Count('id')
        ).order_by('-total')[:5]
        
        if not sales:
            return "Sin ventas"
        
        html = ['<ol style="margin: 0;">']
        for sale in sales:
            html.append(
                f'<li><strong>{sale["customer__name"]}</strong> - '
                f'{sale["count"]} compras (${sale["total"]:,.2f})</li>'
            )
        html.append('</ol>')
        return format_html(''.join(html))
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            sales_count=Count('sale'),
            revenue=Sum('sale__total_price')
        )
        return qs
    
    # Acciones
    
    @admin.action(description='Reabastecer productos (agregar 50 unidades)')
    def restock_products(self, request, queryset):
        updated = queryset.update(in_stock=models.F('in_stock') + 50)
        self.message_user(
            request,
            f'{updated} producto(s) reabastecido(s) con 50 unidades.'
        )
    
    @admin.action(description='Aplicar 10% de descuento')
    def apply_discount(self, request, queryset):
        from django.db.models import F
        updated = queryset.update(price=F('price') * 0.9)
        self.message_user(
            request,
            f'Descuento del 10% aplicado a {updated} producto(s).'
        )
    
    @admin.action(description='Marcar como agotado')
    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(in_stock=0)
        self.message_user(
            request,
            f'{updated} producto(s) marcado(s) como agotado(s).'
        )


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Administrador avanzado para ventas"""
    
    list_display = [
        'id',
        'get_customer_name',
        'get_product_name',
        'quantity',
        'get_total_formatted',
        'get_profit_margin',
        'sale_date'
    ]
    
    list_filter = [
        'sale_date',
        'customer',
        'product__category',
    ]
    
    search_fields = [
        'customer__name',
        'customer__email',
        'product__name'
    ]
    
    readonly_fields = [
        'total_price',
        'sale_date',
        'get_customer_info',
        'get_product_info'
    ]
    
    fieldsets = (
        ('Datos de la Venta', {
            'fields': ('customer', 'product', 'quantity')
        }),
        ('Información Calculada', {
            'fields': ('total_price', 'sale_date'),
            'classes': ('collapse',)
        }),
        ('Detalles', {
            'fields': ('get_customer_info', 'get_product_info'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'sale_date'
    
    actions = ['generate_invoice', 'export_to_csv']
    
    # Métodos personalizados
    
    @admin.display(description='Cliente', ordering='customer__name')
    def get_customer_name(self, obj):
        return format_html(
            '<a href="/admin/sales/customer/{}/change/">{}</a>',
            obj.customer.id,
            obj.customer.name
        )
    
    @admin.display(description='Producto', ordering='product__name')
    def get_product_name(self, obj):
        return format_html(
            '<a href="/admin/sales/product/{}/change/">{}</a>',
            obj.product.id,
            obj.product.name
        )
    
    @admin.display(description='Total', ordering='total_price')
    def get_total_formatted(self, obj):
        if obj.total_price > 1000:
            color = 'green'
        elif obj.total_price > 500:
            color = 'blue'
        else:
            color = 'black'
        return format_html(
            '<strong style="color: {};">${:,.2f}</strong>',
            color,
            obj.total_price
        )
    
    @admin.display(description='Margen')
    def get_profit_margin(self, obj):
        # Suponiendo un costo del 60% del precio
        cost = obj.product.price * 0.6 * obj.quantity
        profit = obj.total_price - cost
        margin = (profit / obj.total_price * 100) if obj.total_price else 0
        
        if margin > 40:
            color = 'green'
        elif margin > 20:
            color = 'blue'
        else:
            color = 'orange'
        
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            margin
        )
    
    @admin.display(description='Info del Cliente')
    def get_customer_info(self, obj):
        total_sales = obj.customer.sales.count()
        total_spent = obj.customer.sales.aggregate(total=Sum('total_price'))['total'] or 0
        
        return format_html(
            '<div style="padding: 10px; background: #f5f5f5; border-radius: 5px;">'
            '<strong>Email:</strong> {}<br>'
            '<strong>Teléfono:</strong> {}<br>'
            '<strong>Total de compras:</strong> {}<br>'
            '<strong>Gasto total:</strong> ${:,.2f}'
            '</div>',
            obj.customer.email,
            obj.customer.phone or 'N/A',
            total_sales,
            total_spent
        )
    
    @admin.display(description='Info del Producto')
    def get_product_info(self, obj):
        return format_html(
            '<div style="padding: 10px; background: #f5f5f5; border-radius: 5px;">'
            '<strong>Precio unitario:</strong> ${:,.2f}<br>'
            '<strong>Categoría:</strong> {}<br>'
            '<strong>Stock actual:</strong> {} unidades'
            '</div>',
            obj.product.price,
            obj.product.category or 'Sin categoría',
            obj.product.in_stock
        )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('customer', 'product')
    
    # Acciones
    
    @admin.action(description='Generar factura')
    def generate_invoice(self, request, queryset):
        count = queryset.count()
        self.message_user(
            request,
            f'Generando facturas para {count} venta(s)... (implementar con WeasyPrint)'
        )
    
    @admin.action(description='Exportar a CSV')
    def export_to_csv(self, request, queryset):
        count = queryset.count()
        self.message_user(
            request,
            f'Exportando {count} venta(s) a CSV... (implementar exportación)'
        )
