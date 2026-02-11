from django.urls import path
from . import views

app_name = 'analytics_api'

urlpatterns = [
    path('kpis/', views.KPIView.as_view(), name='kpis'),
    path('by-period/', views.SalesByPeriodView.as_view(), name='by_period'),
    path('by-category/', views.SalesByCategoryView.as_view(), name='by_category'),
    path('top-customers/', views.TopCustomersView.as_view(), name='top_customers'),
    path('products/', views.ProductDistributionView.as_view(), name='products'),
    path('list/', views.SalesListView.as_view(), name='list'),
]
