from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from sales.models import Customer, Product, Sale


class SchemaAndSalesApiTests(TestCase):
    """Tests básicos para validar que el esquema OpenAPI y la API de ventas responden."""

    def setUp(self):
        self.client = APIClient()

        # Datos mínimos para poder generar ventas
        self.customer = Customer.objects.create(
            name="Cliente Test",
            email="cliente@test.com",
        )
        self.product = Product.objects.create(
            name="Producto Test",
            price="10.00",
            category="Test",
            in_stock=100,
        )
        # Una venta de ejemplo
        Sale.objects.create(
            customer=self.customer,
            product=self.product,
            quantity=2,
        )

    def test_schema_endpoint_returns_200(self):
        """El endpoint de esquema OpenAPI debe devolver 200 y JSON."""
        url = reverse("schema")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # drf-spectacular devuelve JSON; comprobamos que el cuerpo es parseable
        self.assertIsInstance(response.json(), dict)

    def test_kpis_endpoint_returns_200(self):
        """El endpoint de KPIs de ventas debe responder correctamente."""
        url = reverse("analytics_api:kpis")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Comprobaciones básicas de la estructura definida en KPISerializer
        for key in ("total_sales", "total_orders", "average_order", "total_customers"):
            self.assertIn(key, data)

from django.test import TestCase

# Create your tests here.
