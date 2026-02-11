# reports/models.py
from django.db import models
from sales.models import Sale

class Report(models.Model):
    title = models.CharField(max_length=200)
    generated_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/')
    sales = models.ManyToManyField(Sale, related_name="reports")

    def __str__(self):
        return self.title
