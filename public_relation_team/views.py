from django.shortcuts import render


# Create your views here.

def team_home_page(request):
    return render(request,"team_homepage.html")