import reflex as rx

from ..state import DashboardState


def kpi_card(title: str, value: str, subtitle: str | None = None) -> rx.Component:
    """Tarjeta simple para métricas KPI."""
    return rx.box(
        rx.text(title, font_weight="bold", font_size="0.9rem", color="gray.500"),
        rx.text(value, font_weight="bold", font_size="1.5rem"),
        rx.cond(
            subtitle is not None,
            rx.text(subtitle or "", font_size="0.8rem", color="gray.500"),
        ),
        padding="1rem",
        border_radius="lg",
        border="1px solid",
        border_color="gray.200",
        background_color="white",
        box_shadow="sm",
        min_width="200px",
    )


def kpi_section() -> rx.Component:
    s = DashboardState  # alias corto
    total_sales = rx.cond(
        s.kpis.get("total_sales").equals(None),
        "0",
        s.kpis.get("total_sales").to(str),
    )
    total_orders = rx.cond(
        s.kpis.get("total_orders").equals(None),
        "0",
        s.kpis.get("total_orders").to(str),
    )
    average_order = rx.cond(
        s.kpis.get("average_order").equals(None),
        "0",
        s.kpis.get("average_order").to(str),
    )
    total_customers = rx.cond(
        s.kpis.get("total_customers").equals(None),
        "0",
        s.kpis.get("total_customers").to(str),
    )

    return rx.vstack(
        rx.heading("Resumen de KPIs", size="md"),
        rx.hstack(
            kpi_card("Ventas totales", total_sales),
            kpi_card("Pedidos", total_orders),
            kpi_card("Ticket medio", average_order),
            kpi_card("Clientes únicos", total_customers),
            spacing="1rem",
            wrap="wrap",
        ),
        spacing="0.75rem",
        align_items="flex-start",
        width="100%",
    )


def table_by_period() -> rx.Component:
    return rx.vstack(
        rx.heading("Ventas por periodo", size="sm"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Periodo"),
                    rx.table.column_header_cell("Total"),
                    rx.table.column_header_cell("Nº pedidos"),
                )
            ),
            rx.table.body(
                rx.foreach(
                    DashboardState.by_period,
                    lambda row: rx.table.row(
                        rx.table.cell(row["period"]),
                        rx.table.cell(row["total"]),
                        rx.table.cell(row["count"]),
                    ),
                )
            ),
            size="sm",
            variant="outline",
        ),
        padding="1rem",
        border_radius="lg",
        border="1px solid",
        border_color="gray.200",
        background_color="white",
        box_shadow="sm",
        width="100%",
    )


def table_by_category() -> rx.Component:
    return rx.vstack(
        rx.heading("Ventas por categoría", size="sm"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Categoría"),
                    rx.table.column_header_cell("Total"),
                    rx.table.column_header_cell("Nº pedidos"),
                )
            ),
            rx.table.body(
                rx.foreach(
                    DashboardState.by_category,
                    lambda row: rx.table.row(
                        rx.table.cell(row["category"]),
                        rx.table.cell(row["total"]),
                        rx.table.cell(row["count"]),
                    ),
                )
            ),
            size="sm",
            variant="outline",
        ),
        padding="1rem",
        border_radius="lg",
        border="1px solid",
        border_color="gray.200",
        background_color="white",
        box_shadow="sm",
        width="100%",
    )


def table_top_customers() -> rx.Component:
    return rx.vstack(
        rx.heading("Top clientes", size="sm"),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Cliente"),
                    rx.table.column_header_cell("Importe total"),
                    rx.table.column_header_cell("Pedidos"),
                )
            ),
            rx.table.body(
                rx.foreach(
                    DashboardState.top_customers,
                    lambda row: rx.table.row(
                        rx.table.cell(row["customer_name"]),
                        rx.table.cell(row["total_spent"]),
                        rx.table.cell(row["order_count"]),
                    ),
                )
            ),
            size="sm",
            variant="outline",
        ),
        padding="1rem",
        border_radius="lg",
        border="1px solid",
        border_color="gray.200",
        background_color="white",
        box_shadow="sm",
        width="100%",
    )


def index() -> rx.Component:
    """Página principal del dashboard Reflex."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading("RevIntel", size="lg"),
                rx.spacer(),
                rx.badge("Reflex UI", color_scheme="purple"),
                align_items="center",
                width="100%",
            ),
            rx.cond(
                DashboardState.loading,
                rx.text("Cargando datos...", color="gray.500"),
                rx.fragment(),
            ),
            rx.cond(
                DashboardState.error != "",
                rx.alert(
                    rx.alert_icon(),
                    rx.alert_title("Error al cargar el dashboard"),
                    rx.alert_description(DashboardState.error),
                    status="error",
                ),
                rx.fragment(),
            ),
            kpi_section(),
            rx.hstack(
                table_by_period(),
                table_by_category(),
                spacing="1rem",
                align_items="flex-start",
                wrap="wrap",
                width="100%",
            ),
            table_top_customers(),
            spacing="1.5rem",
            padding="1.5rem",
            max_width="1200px",
            margin_x="auto",
        ),
        background_color="gray.50",
        min_height="100vh",
        padding_y="2rem",
    )

