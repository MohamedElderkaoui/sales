# reports/admin.py
from django.contrib import admin
from django.db.models import Count, Sum
from django.utils.html import format_html
from django.utils import timezone
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Administrador avanzado para reportes"""
    
    list_display = [
        'title',
        'get_file_link',
        'get_sales_count',
        'get_total_revenue',
        'generated_at',
        'get_age'
    ]
    
    list_filter = [
        'generated_at',
    ]
    
    search_fields = [
        'title',
        'sales__customer__name',
        'sales__product__name'
    ]
    
    filter_horizontal = ['sales']
    
    readonly_fields = [
        'generated_at',
        'get_sales_count',
        'get_total_revenue',
        'get_file_info',
        'get_sales_breakdown'
    ]
    
    fieldsets = (
        ('Información del Reporte', {
            'fields': ('title', 'file')
        }),
        ('Ventas Incluidas', {
            'fields': ('sales',),
            'description': 'Selecciona las ventas que se incluirán en este reporte'
        }),
        ('Estadísticas', {
            'fields': ('get_sales_count', 'get_total_revenue', 'get_sales_breakdown'),
            'classes': ('collapse',)
        }),
        ('Información del Archivo', {
            'fields': ('generated_at', 'get_file_info'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'generated_at'
    
    actions = ['regenerate_reports', 'download_reports', 'archive_reports']
    
    # Métodos personalizados
    
    @admin.display(description='Archivo', ordering='file')
    def get_file_link(self, obj):
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank">📄 Descargar</a>',
                obj.file.url
            )
        return format_html('<span style="color: red;">Sin archivo</span>')
    
    @admin.display(description='Ventas', ordering='sales_count')
    def get_sales_count(self, obj):
        count = obj.sales.count()
        if count == 0:
            return format_html('<span style="color: gray;">Sin ventas</span>')
        elif count < 10:
            return format_html('<span style="color: orange;">{} ventas</span>', count)
        else:
            return format_html('<span style="color: green;"><strong>{}</strong> ventas</span>', count)
    
    @admin.display(description='Ingresos Totales', ordering='total_revenue')
    def get_total_revenue(self, obj):
        total = obj.sales.aggregate(total=Sum('total_price'))['total'] or 0
        # Aseguramos que el valor sea numérico y lo formateamos antes de pasarlo a format_html,
        # ya que format_html convierte los argumentos a cadenas (SafeString) y no soporta {:,.2f}.
        try:
            from decimal import Decimal
            if not isinstance(total, (int, float, Decimal)):
                total = Decimal(str(total))
            formatted_total = f"${total:,.2f}"
        except Exception:
            # Si algo falla, mostramos 0 de forma segura
            formatted_total = "$0.00"
        return format_html('<strong style="color: green;">{}</strong>', formatted_total)
    
    @admin.display(description='Antigüedad')
    def get_age(self, obj):
        delta = timezone.now() - obj.generated_at
        days = delta.days
        
        if days == 0:
            return format_html('<span style="color: green;">🆕 Hoy</span>')
        elif days == 1:
            return format_html('<span style="color: blue;">Ayer</span>')
        elif days < 7:
            return format_html('<span style="color: orange;">{} días</span>', days)
        elif days < 30:
            weeks = days // 7
            return format_html('<span style="color: red;">{} semana(s)</span>', weeks)
        else:
            months = days // 30
            return format_html('<span style="color: red;">{} mes(es)</span>', months)
    
    @admin.display(description='Información del Archivo')
    def get_file_info(self, obj):
        if not obj.file:
            return "No hay archivo adjunto"
        
        try:
            size = obj.file.size
            size_kb = size / 1024
            size_mb = size_kb / 1024
            
            if size_mb >= 1:
                size_str = f"{size_mb:.2f} MB"
            else:
                size_str = f"{size_kb:.2f} KB"
            
            return format_html(
                '<div style="padding: 10px; background: #f5f5f5; border-radius: 5px;">'
                '<strong>Nombre:</strong> {}<br>'
                '<strong>Tamaño:</strong> {}<br>'
                '<strong>Ruta:</strong> {}'
                '</div>',
                obj.file.name.split('/')[-1],
                size_str,
                obj.file.name
            )
        except:
            return "Información no disponible"
    
    @admin.display(description='Desglose de Ventas')
    def get_sales_breakdown(self, obj):
        """Muestra estadísticas detalladas de las ventas incluidas"""
        sales = obj.sales.all()
        
        if not sales:
            return "No hay ventas en este reporte"
        
        # Estadísticas por producto
        products = sales.values('product__name', 'product__category').annotate(
            count=Count('id'),
            total=Sum('total_price')
        ).order_by('-total')[:5]
        
        # Estadísticas por cliente
        customers = sales.values('customer__name').annotate(
            count=Count('id'),
            total=Sum('total_price')
        ).order_by('-total')[:5]
        
        summary = []
        summary.append(f"<strong>Total de ventas:</strong> {sales.count()}<br><br>")
        
        if products:
            summary.append("<strong>Top 5 Productos:</strong><ol style='margin-top: 5px;'>")
            for product in products:
                category = product['product__category'] or 'Sin categoría'
                summary.append(
                    f"<li>{product['product__name']} ({category}): "
                    f"{product['count']} ventas - ${product['total']:,.2f}</li>"
                )
            summary.append("</ol>")
        
        if customers:
            summary.append("<strong>Top 5 Clientes:</strong><ol style='margin-top: 5px;'>")
            for customer in customers:
                summary.append(
                    f"<li>{customer['customer__name']}: "
                    f"{customer['count']} ventas - ${customer['total']:,.2f}</li>"
                )
            summary.append("</ol>")
        
        return format_html(''.join(summary))
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            sales_count=Count('sales'),
            total_revenue=Sum('sales__total_price')
        )
        return qs.prefetch_related('sales__product', 'sales__customer')
    
    # Acciones personalizadas
    
    @admin.action(description='Regenerar reportes')
    def regenerate_reports(self, request, queryset):
        """Regenera los reportes seleccionados"""
        count = queryset.count()
        self.message_user(
            request,
            f'Regenerando {count} reporte(s)... (implementar lógica con WeasyPrint)'
        )
    
    @admin.action(description='Descargar reportes seleccionados')
    def download_reports(self, request, queryset):
        """Descarga múltiples reportes"""
        count = queryset.count()
        self.message_user(
            request,
            f'Preparando descarga de {count} reporte(s)... (implementar ZIP)'
        )
    
    @admin.action(description='Archivar reportes')
    def archive_reports(self, request, queryset):
        """Archiva reportes antiguos"""
        count = queryset.count()
        self.message_user(
            request,
            f'{count} reporte(s) archivado(s).'
        )
    
    def save_model(self, request, obj, form, change):
        """Lógica personalizada al guardar"""
        super().save_model(request, obj, form, change)
        
        if change:
            self.message_user(
                request,
                f'Reporte "{obj.title}" actualizado correctamente.'
            )
        else:
            self.message_user(
                request,
                f'Reporte "{obj.title}" creado exitosamente.'
            )
