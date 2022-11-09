from django.shortcuts import render
from django.http.response import HttpResponse,JsonResponse
from users.models import Members
from api.serializers import MembersSerializer
from rest_framework.generics import ListAPIView
from django.views.decorators.csrf import csrf_exempt
from . import OnAppAuth
from django.db import DatabaseError
# Create your views here.


#Creating the api to signup users here
@csrf_exempt
def signupAppUser(request):
    if request.method=="POST":
        email=request.POST.get("email_ieee")
        try:
            result=OnAppAuth.OnAppProcesses.signup(email=email)
            if(result==DatabaseError):
                return JsonResponse({"status":"database-failure"})
            elif(result=="Already Signedup"):
                return JsonResponse({"status":"already-signedup"})
            elif(result=="success"):
                data=OnAppAuth.OnAppProcesses.getUserData(email=email)
                return JsonResponse(data=data)
                
        except:
            return JsonResponse({"status":"code-failure"})
    else:
        return JsonResponse({"status":"connection-not secured"})

    