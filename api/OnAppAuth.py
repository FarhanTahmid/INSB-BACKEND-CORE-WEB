from users.models import Members
from django.http import HttpResponseServerError
from django.db import DatabaseError
from django.contrib.auth.models import User,auth
class OnAppProcesses:
    def __init__(self) -> None:
        pass
    def signup(email):
        try:
            user:Members=Members.objects.get(email_ieee=email) #getting the user from our database
        except:
            return DatabaseError
        try:
            username=user.ieee_id
            password='ieee@nSuSb' #Using a default pass at firs
            if(User.objects.filter(username=username)):
                return "Already Signedup"
            else:
                registeredUser=User.objects.create_user(username=username,email=email,password=password)
                registeredUser.save()
                return "success"
        except:
            return DatabaseError
     
    
    def getUserData(email):
        user:Members=Members.objects.get(email_ieee=email)
        memberDataDict={
                "status":"success",
                "ieee_id":user.ieee_id,
                "name":user.name,
                "nsu_id":user.nsu_id,
                "email_ieee":user.email_ieee,
                "email_personal":user.email_personal,
                "contact_no":user.contact_no,
                "home_address":user.home_address,
                "date_of_birth":user.date_of_birth,
                "gender":user.gender,
                "facebook_url":user.facebook_url,
                "team":str(user.team),
                "position":str(user.position)
        }
        return memberDataDict