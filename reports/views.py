# reports/views.py
import csv
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Sum, Count
from weasyprint import HTML

from sales.models import Sale
from analytics.views import SaleFilter


def export_csv(request):
    """Exportar ventas a CSV"""
    queryset = Sale.objects.select_related('customer', 'product').all()
    filterset = SaleFilter(request.GET, queryset=queryset)
    sales = filterset.qs.order_by('-sale_date')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ventas_reporte.csv"'
    response.write('\ufeff')  # BOM para Excel
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Fecha', 'Cliente', 'Producto', 'Categoría', 'Cantidad', 'Total'])
    
    for sale in sales:
        writer.writerow([
            sale.id,
            sale.sale_date.strftime('%Y-%m-%d %H:%M'),
            sale.customer.name,
            sale.product.name,
            sale.product.category or '-',
            sale.quantity,
            float(sale.total_price)
        ])
    
    return response


def export_pdf(request):
    """Exportar reporte a PDF con WeasyPrint"""
    queryset = Sale.objects.select_related('customer', 'product').all()
    filterset = SaleFilter(request.GET, queryset=queryset)
    sales = filterset.qs.order_by('-sale_date')[:100]  # Limitar para PDF
    
    # Calcular totales
    aggregates = filterset.qs.aggregate(
        total_sales=Sum('total_price'),
        total_orders=Count('id')
    )
    
    # Ventas por categoría
    by_category = filterset.qs.values('product__category').annotate(
        total=Sum('total_price'),
        count=Count('id')
    ).order_by('-total')[:5]
    
    context = {
        'sales': sales,
        'total_sales': aggregates['total_sales'] or 0,
        'total_orders': aggregates['total_orders'] or 0,
        'by_category': by_category,
        'filters': dict(request.GET),
    }
    
    html_string = render_to_string('reports/pdf_template.html', context)
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.pdf"'
    return response
