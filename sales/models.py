from decimal import Decimal
from django.db import models, transaction
from django.core.validators import MinValueValidator
from django.utils import timezone

class Customer(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_at"]


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank=True)
    in_stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="sales")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sales")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False, blank=True)
    sale_date = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        # Aseguramos Decimal y dos decimales
        return (self.product.price * Decimal(self.quantity)).quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        # Calcula total_price
        self.total_price = self.calculate_total()

        # Manejo de stock: ajusta solo en creación / actualización con diferencia
        with transaction.atomic():
            if self.pk is None:
                # nueva venta -> verificar stock y descontar
                if self.quantity > self.product.in_stock:
                    from django.core.exceptions import ValidationError
                    raise ValidationError("No hay stock suficiente para este producto.")
                self.product.in_stock = models.F('in_stock') - self.quantity
                self.product.save(update_fields=['in_stock'])
            else:
                # actualización: ajustar diferencia
                old = Sale.objects.select_for_update().get(pk=self.pk)
                diff = self.quantity - old.quantity
                if diff != 0:
                    if diff > 0 and diff > self.product.in_stock:
                        from django.core.exceptions import ValidationError
                        raise ValidationError("No hay stock suficiente para aumentar la cantidad.")
                    # usar F() para concurrencia segura
                    self.product.in_stock = models.F('in_stock') - diff
                    self.product.save(update_fields=['in_stock'])

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.name} - {self.product.name} x {self.quantity}"

    class Meta:
        ordering = ["-sale_date"]
