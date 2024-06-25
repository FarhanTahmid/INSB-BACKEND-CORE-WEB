from django.shortcuts import render, HttpResponse
from firebase_admin import messaging,exceptions
from . import firebase_admin


def send_push_notification(token, title, body):

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token
    )
    response = messaging.send(message)
    return response
    

