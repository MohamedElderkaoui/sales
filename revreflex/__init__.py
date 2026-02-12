import os

import reflex as rx

from . import state
from .pages.index import index


def get_api_base() -> str:
    """Obtiene la URL base del backend Django.

    Por defecto: http://localhost:8000
    Se puede sobreescribir con la variable de entorno REVINTEL_API_BASE.
    """
    return os.environ.get("REVINTEL_API_BASE", "http://localhost:8000").rstrip("/")


# Guardamos la URL base en el state para reutilizarla.
state.API_BASE = get_api_base()


app = rx.App()
app.add_page(
    index,
    route="/",
    title="RevIntel - Dashboard de ventas",
    on_load=state.DashboardState.load_data,
)
app.compile()

