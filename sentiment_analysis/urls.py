from django.urls import path
from . import views

app_name = 'sentiment_analysis'  # Optional but good practice for namespacing

urlpatterns = [
    path('', views.analyze, name='analyze'),
]