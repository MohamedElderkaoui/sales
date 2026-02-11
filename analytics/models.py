# analytics/models.py
from django.db import models
from django.utils.timezone import now
from sales.models import Sale

class SalesMetric(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE)
    revenue = models.DecimalField(max_digits=12, decimal_places=2)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Metric for Sale ID {self.sale.id}"


class DashboardFilter(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
