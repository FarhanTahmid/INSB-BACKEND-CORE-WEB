from django.shortcuts import render

# Create your views here.

def pes_homepage(request):
    return render(request,'PES/homepage.html')