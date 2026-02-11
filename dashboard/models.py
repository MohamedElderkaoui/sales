# dashboard/models.py
from django.db import models
from sales.models import Sale

class GraphConfig(models.Model):
    name = models.CharField(max_length=100)
    chart_type = models.CharField(max_length=50, choices=(
        ("bar", "Bar"),
        ("line", "Line"),
        ("pie", "Pie")
    ), default="bar")
    sales = models.ManyToManyField(Sale, related_name="graphs")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
