from django.shortcuts import render
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Create your views here.

def team_home_page(request):
    return render(request,"team_homepage.html")

