from django.shortcuts import render, HttpResponse
from firebase_admin import messaging,exceptions
from . import firebase_admin
from .models import *


def send_push_notification(title,body,token):

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token
    )
    response = messaging.send(message)
    return response
    
def save_token(member,token):

    '''This function saves the token for each user,regardless of what browser they use'''

    member_token = PushNotification.objects.filter(member = member)
    found = False
    for mbm_tkn in member_token:
        if mbm_tkn.fcm_token == token:
            found = True
            print("token exists")
            print(token)
            break
    if not found:
        new_token = PushNotification.objects.create(member = member,fcm_token = token)
        new_token.save()
        print("token saved")
    return True
