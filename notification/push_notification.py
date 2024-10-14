from django.shortcuts import render, HttpResponse
from firebase_admin import messaging,exceptions
from . import firebase_admin
from .models import *
from datetime import datetime


def send_push_notification(title,body,token,link=None):

    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
            data={"link": link} if link else None
        )
        response = messaging.send(message)
        return response 
    except:
        print("going to delete token since does not exist")
        remove_token_from_db(token)
    
def save_token(member,token):

    '''This function saves the token for each user,regardless of what browser they use'''
    try:
        member_token = PushNotification.objects.get(member = member)
        if token != member_token.fcm_token:
            member_token.fcm_token = token
            member_token.updated_at = datetime.now()
            member_token.save()
    except:
        member_token = PushNotification.objects.create(member = member,fcm_token = token,created_at = datetime.now(),updated_at = datetime.now())
        member_token.save()
    return True


def remove_token_from_db(token):

    """
    Removes the PushNotification entry with the given token.
    """
    
    try:
        push_notification = PushNotification.objects.get(fcm_token=token)
        push_notification.delete()
        print("token deleted")
    except PushNotification.DoesNotExist:
        print("token does not exist for deleting")
    except Exception as e:
        print("error occures during token deletion")