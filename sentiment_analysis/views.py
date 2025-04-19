# sentiment_analysis/views.py

from django.http import JsonResponse
from django.shortcuts import render
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

model_name = "yiyanghkust/finbert-tone"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def predict_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=1).numpy()[0]
    labels = ['negative', 'neutral', 'positive']
    sentiment = labels[np.argmax(probabilities)]
    confidence = probabilities[np.argmax(probabilities)]
    return sentiment, confidence

def analyze(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        sentiment, confidence = predict_sentiment(text)
        return JsonResponse({
            'sentiment': sentiment,
            'confidence': f'{confidence:.2f}'
        })
    return render(request, 'analyze.html')  # Make sure this path is correct
