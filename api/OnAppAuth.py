from users.models import Members
from django.http import HttpResponseServerError
from django.db import DatabaseError
class OnAppProcesses:
    def __init__(self) -> None:
        pass
    def signup(email):
        try:
            user:Members=Members.objects.get(email_ieee=email) #getting the user from our database
        except:
            return DatabaseError
        try:
            pass
        except:
            return DatabaseError