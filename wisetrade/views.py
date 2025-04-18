from django.shortcuts import render
from django.http import HttpResponse

def homepage(request):
<<<<<<< HEAD
    return HttpResponse("HomePage!")
=======
    return render(request,'homepage.html')
>>>>>>> 83a97cbb0df2e8e6be15a026c1e5c13abcd467c0
