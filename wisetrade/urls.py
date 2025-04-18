# project_name/urls.py

from django.contrib import admin
from django.urls import path, include

from technical_analysis.views import fetch as technical_analysis_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),  # Homepage handled by dashboard
    path('api/technical/', technical_analysis_view, name='technical_analysis'),
]
