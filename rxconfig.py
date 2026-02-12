import reflex as rx


class RevintelConfig(rx.Config):
    """Configuración principal de la app Reflex."""

    # Nombre interno de la app (carpeta Python).
    app_name: str = "revreflex"

    # Puertos por defecto. Ajusta si ya usas estos en Django.
    frontend_port: int = 3000
    backend_port: int = 8001

    # URL base del backend Django que expone /api/sales/...
    api_url: str = "http://localhost:8000"

    # Orígenes permitidos para CORS cuando llames al backend.
    cors_allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

config = RevintelConfig(app_name="revreflex")
