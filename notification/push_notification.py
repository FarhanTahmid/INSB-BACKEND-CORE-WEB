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
    try:
        member_token = PushNotification.objects.get(member = member)
        member_token.fcm_token = token
        member_token.save()
    except:
        member_token = PushNotification.objects.create(member = member,fcm_token = token)
        member_token.save()
    return True
