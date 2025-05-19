from django.shortcuts import render
from django.http import HttpResponse

def homepage(request):
    return HttpResponse("HomePage!")
    return render(request,'homepage.html')
