from django.db import models

# Create your models here.
# models.py

class Company(models.Model):
    name = models.CharField(max_length=255)
    ticker_symbol = models.CharField(max_length=10, unique=True)

class AssetType(models.Model):
    name = models.CharField(max_length=100)  # e.g., "Factory", "HQ"
    default_sensitivities = models.JSONField(default=list)

class Asset(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    asset_type = models.ForeignKey(AssetType, on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=255)
    coordinates = models.JSONField(null=True, blank=True)  # {'lat': 28.6, 'lng': 77.2}
    importance = models.CharField(choices=[("high", "High"), ("medium", "Medium"), ("low", "Low")], max_length=10)
    custom_sensitivities = models.JSONField(default=list, blank=True)

class Event(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    location = models.CharField(max_length=255)
    coordinates = models.JSONField(null=True, blank=True)
    event_type = models.CharField(max_length=100)
    date = models.DateTimeField()
    sentiment = models.CharField(choices=[("positive", "Positive"), ("neutral", "Neutral"), ("negative", "Negative")], max_length=10)
    matched_assets = models.ManyToManyField(Asset)

class StockImpact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    predicted_impact = models.CharField(choices=[("positive", "📈 Positive"), ("neutral", "⚪ Neutral"), ("negative", "📉 Negative")], max_length=10)
    confidence_score = models.FloatField()
