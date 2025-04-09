# project_name/urls.py

from django.contrib import admin
from django.urls import path, include
from dashboard.views import price_data_view
from technical_analysis.views import fetch as technical_analysis_view
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('api/price_data/', price_data_view, name='price_data'),
    path('api/technical/', technical_analysis_view, name='technical_analysis'),
]
