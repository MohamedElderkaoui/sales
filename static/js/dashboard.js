// dashboard.js - Lógica del dashboard analítico

const API_BASE = '/api/sales';
let charts = {};
let currentPage = 1;
let currentFilters = {};

// Utilidades
const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'USD' }).format(value);
};

const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('es-ES');
};

const buildQueryString = (params) => {
    const filtered = Object.entries(params).filter(([_, v]) => v !== '' && v !== null);
    return filtered.length ? '?' + new URLSearchParams(filtered).toString() : '';
};

// Colores para gráficos
const chartColors = [
    '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
    '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b'
];

// ============ API CALLS ============

async function fetchKPIs() {
    const query = buildQueryString(currentFilters);
    const res = await fetch(`${API_BASE}/kpis/${query}`);
    return res.json();
}

async function fetchSalesByPeriod(groupBy = 'day') {
    const params = { ...currentFilters, group_by: groupBy };
    const query = buildQueryString(params);
    const res = await fetch(`${API_BASE}/by-period/${query}`);
    return res.json();
}

async function fetchSalesByCategory() {
    const query = buildQueryString(currentFilters);
    const res = await fetch(`${API_BASE}/by-category/${query}`);
    return res.json();
}

async function fetchTopCustomers() {
    const query = buildQueryString({ ...currentFilters, limit: 10 });
    const res = await fetch(`${API_BASE}/top-customers/${query}`);
    return res.json();
}

async function fetchProductDistribution() {
    const query = buildQueryString({ ...currentFilters, limit: 10 });
    const res = await fetch(`${API_BASE}/products/${query}`);
    return res.json();
}

async function fetchSalesList(page = 1) {
    const params = { ...currentFilters, page, per_page: 15 };
    const query = buildQueryString(params);
    const res = await fetch(`${API_BASE}/list/${query}`);
    return res.json();
}

// ============ UI UPDATES ============

function updateKPIs(data) {
    document.getElementById('kpi-total-sales').textContent = formatCurrency(data.total_sales);
    document.getElementById('kpi-total-orders').textContent = data.total_orders.toLocaleString();
    document.getElementById('kpi-average-order').textContent = formatCurrency(data.average_order);
    document.getElementById('kpi-total-customers').textContent = data.total_customers.toLocaleString();
}

function updateLastUpdate() {
    const now = new Date().toLocaleString('es-ES');
    document.querySelector('#last-update span').textContent = now;
}

// ============ CHARTS ============

function createTrendChart(data) {
    const ctx = document.getElementById('sales-trend-chart').getContext('2d');
    
    if (charts.trend) charts.trend.destroy();
    
    charts.trend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.period),
            datasets: [{
                label: 'Ventas ($)',
                data: data.map(d => parseFloat(d.total)),
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                fill: true,
                tension: 0.3
            }, {
                label: 'Órdenes',
                data: data.map(d => d.count),
                borderColor: '#e74c3c',
                backgroundColor: 'transparent',
                yAxisID: 'y1',
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            scales: {
                y: { beginAtZero: true, position: 'left' },
                y1: { beginAtZero: true, position: 'right', grid: { drawOnChartArea: false } }
            }
        }
    });
}

function createCategoryChart(data) {
    const ctx = document.getElementById('category-chart').getContext('2d');
    
    if (charts.category) charts.category.destroy();
    
    charts.category = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(d => d.category),
            datasets: [{
                data: data.map(d => parseFloat(d.total)),
                backgroundColor: chartColors
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right' }
            }
        }
    });
}

function createProductsChart(data) {
    const ctx = document.getElementById('products-chart').getContext('2d');
    
    if (charts.products) charts.products.destroy();
    
    charts.products = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.product_name),
            datasets: [{
                label: 'Ingresos ($)',
                data: data.map(d => parseFloat(d.revenue)),
                backgroundColor: chartColors
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false } }
        }
    });
}

function createCustomersChart(data) {
    const ctx = document.getElementById('customers-chart').getContext('2d');
    
    if (charts.customers) charts.customers.destroy();
    
    charts.customers = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.customer_name),
            datasets: [{
                label: 'Total gastado ($)',
                data: data.map(d => parseFloat(d.total_spent)),
                backgroundColor: '#3498db'
            }, {
                label: 'Órdenes',
                data: data.map(d => d.order_count),
                backgroundColor: '#2ecc71'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } }
        }
    });
}

// ============ TABLE ============

function updateTable(response) {
    const tbody = document.getElementById('sales-table-body');
    tbody.innerHTML = '';
    
    if (!response.data || response.data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No hay datos disponibles</td></tr>';
        return;
    }
    
    response.data.forEach(sale => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${sale.id}</td>
            <td>${formatDate(sale.sale_date)}</td>
            <td>${sale.customer_name}</td>
            <td>${sale.product_name}</td>
            <td>${sale.product_category || '-'}</td>
            <td>${sale.quantity}</td>
            <td>${formatCurrency(sale.total_price)}</td>
        `;
        tbody.appendChild(row);
    });
    
    // Actualizar paginación
    document.getElementById('page-info').textContent = 
        `Página ${response.page} de ${response.total_pages}`;
    document.getElementById('prev-page').disabled = response.page <= 1;
    document.getElementById('next-page').disabled = response.page >= response.total_pages;
    currentPage = response.page;
}

// ============ DATA LOADING ============

async function loadAllData() {
    try {
        const [kpis, trend, categories, products, customers, sales] = await Promise.all([
            fetchKPIs(),
            fetchSalesByPeriod(document.getElementById('period-selector').value),
            fetchSalesByCategory(),
            fetchProductDistribution(),
            fetchTopCustomers(),
            fetchSalesList(currentPage)
        ]);
        
        updateKPIs(kpis);
        createTrendChart(trend);
        createCategoryChart(categories);
        createProductsChart(products);
        createCustomersChart(customers);
        updateTable(sales);
        updateLastUpdate();
    } catch (error) {
        console.error('Error cargando datos:', error);
    }
}

// ============ FILTERS ============

function getFiltersFromForm() {
    const form = document.getElementById('filters-form');
    const formData = new FormData(form);
    const filters = {};
    
    for (const [key, value] of formData.entries()) {
        if (value) filters[key] = value;
    }
    
    return filters;
}

function clearFilters() {
    document.getElementById('filters-form').reset();
    currentFilters = {};
    currentPage = 1;
    loadAllData();
}

// ============ EXPORT ============

function updateExportLinks() {
    const query = buildQueryString(currentFilters);
    document.getElementById('export-csv').href = `/reports/export/csv/${query}`;
    document.getElementById('export-pdf').href = `/reports/export/pdf/${query}`;
}

// ============ EVENT LISTENERS ============

document.addEventListener('DOMContentLoaded', () => {
    // Carga inicial
    loadAllData();
    updateExportLinks();
    
    // Filtros
    document.getElementById('filters-form').addEventListener('submit', (e) => {
        e.preventDefault();
        currentFilters = getFiltersFromForm();
        currentPage = 1;
        loadAllData();
        updateExportLinks();
    });
    
    document.getElementById('clear-filters').addEventListener('click', clearFilters);
    
    // Selector de período
    document.getElementById('period-selector').addEventListener('change', async (e) => {
        const data = await fetchSalesByPeriod(e.target.value);
        createTrendChart(data);
    });
    
    // Paginación
    document.getElementById('prev-page').addEventListener('click', async () => {
        if (currentPage > 1) {
            const data = await fetchSalesList(currentPage - 1);
            updateTable(data);
        }
    });
    
    document.getElementById('next-page').addEventListener('click', async () => {
        const data = await fetchSalesList(currentPage + 1);
        updateTable(data);
    });
    
    // Búsqueda en tabla (debounce)
    let searchTimeout;
    document.getElementById('table-search').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(async () => {
            currentFilters.search = e.target.value;
            currentPage = 1;
            const data = await fetchSalesList(1);
            updateTable(data);
        }, 300);
    });
});
