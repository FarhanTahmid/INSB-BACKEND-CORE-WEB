from django.shortcuts import render, HttpResponse
from firebase_admin import messaging,exceptions
from . import firebase_admin


def send_push_notification(token, title, body):
    print("here")
    print(token)
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token
    )
    print("end")
    try:
        response = messaging.send(message)
        print('Successfully sent message:', response)
    except exceptions.FirebaseError as e:
        pass
    except Exception as e:
        pass

