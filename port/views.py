from django.shortcuts import render
import datetime


# Create your views here.
def homepage(request):
    return render(request,'port/landing_page.html')