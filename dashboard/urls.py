# dashboard/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard_view/', views.dashboard_view, name='dashboard_view'),
    path('api/price_data', views.price_data_api, name='price_data_api'),
]
