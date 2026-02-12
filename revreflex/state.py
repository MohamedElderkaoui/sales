from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

import reflex as rx
import requests

logger = logging.getLogger(__name__)

# Se inicializa desde revreflex.__init__.py
API_BASE: str = os.environ.get("REVINTEL_API_BASE", "http://localhost:8000").rstrip("/")


class DashboardState(rx.State):
    """Estado principal del dashboard de ventas."""

    loading: bool = False
    error: str = ""

    kpis: Dict[str, Any] = {}
    by_period: List[Dict[str, Any]] = []
    by_category: List[Dict[str, Any]] = []
    top_customers: List[Dict[str, Any]] = []

    def _get(self, path: str, params: Dict[str, Any] | None = None) -> Any:
        """Helper simple para llamar al backend Django."""
        url = f"{API_BASE}{path}"
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def load_data(self):
        """Carga todos los datos iniciales del dashboard."""
        self.loading = True
        self.error = ""

        try:
            # KPIs generales
            self.kpis = self._get("/api/sales/kpis/")

            # Serie temporal por día (se puede cambiar a month si quieres)
            self.by_period = self._get("/api/sales/by-period/", params={"group_by": "day"})

            # Por categoría de producto
            self.by_category = self._get("/api/sales/by-category/")

            # Top clientes
            self.top_customers = self._get("/api/sales/top-customers/", params={"limit": 10})

        except Exception as exc:  # noqa: BLE001
            logger.exception("Error al cargar datos del dashboard")
            self.error = str(exc)
        finally:
            self.loading = False

