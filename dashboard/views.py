from django.shortcuts import render
from sales.models import Product, Customer


def dashboard_view(request):
    """Vista principal del dashboard"""
    context = {
        'products': Product.objects.all(),
        'customers': Customer.objects.all(),
        'categories': Product.objects.values_list('category', flat=True).distinct(),
    }
    return render(request, 'dashboard/index.html', context)
