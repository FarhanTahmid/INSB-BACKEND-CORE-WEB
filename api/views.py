from django.shortcuts import render
from django.http.response import HttpResponse
from users.models import Members
from api.serializers import MembersSerializer
from rest_framework.generics import ListAPIView
from django.views.decorators.csrf import csrf_exempt
from . import OnAppAuth
# Create your views here.


#Creating the api to signup users here
@csrf_exempt
def signupAppUser(request):
    if request.method=="POST":
        email=request.POST.get("email_ieee")
        OnAppAuth.OnAppProcesses.signup(email=email)
        
    else:
        print("hocche na bhaia")
    return HttpResponse("hoise connect")