# sentiment_analysis/sentiment_analyzer.py

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

model_name = "yiyanghkust/finbert-tone"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def analyze_sentiment(text):
    # print("Hitting FINBERT Model")
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True,max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=1).numpy()[0]
    labels = ['negative', 'neutral', 'positive']
    sentiment = labels[np.argmax(probabilities)]
    # print(sentiment)
    return sentiment
