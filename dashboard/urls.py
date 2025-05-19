# dashboard/urls.py


from django.urls import path
from . import views
from technical_analysis.views import technical_analysis_page

urlpatterns = [
    path('', views.home,            name='home'),       # new entry
    path('signup/',  views.signup,            name='signup'),
    path('login/',   views.login_view,        name='login'),
    path('logout/',  views.logout_view,       name='logout'),
    path('dashboard/', views.dashboard_view,  name='dashboard'),
    path('api/price_data', views.price_data_api, name='price_data_api'),
    path('technical/', technical_analysis_page, name='technical_analysis_page'),
]

