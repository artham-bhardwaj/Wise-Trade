# project_name/urls.py

from django.contrib import admin
from django.urls import path, include
<<<<<<< HEAD

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
=======
from dashboard.views import price_data_view
from technical_analysis.views import fetch as technical_analysis_view
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('api/price_data/', price_data_view, name='price_data'),
    path('api/technical/', technical_analysis_view, name='technical_analysis'),
>>>>>>> 83a97cbb0df2e8e6be15a026c1e5c13abcd467c0
]
