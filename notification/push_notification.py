from django.shortcuts import render, HttpResponse
from firebase_admin import messaging,exceptions
from . import firebase_admin
from .models import *


def send_push_notification(member_notifications_count,token):

    title = "IEEE NSU SB PORTAL"
    body = f"You have {str(member_notifications_count)} new notifications!"
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token
    )
    response = messaging.send(message)
    return response
    

