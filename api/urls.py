import imp
from django.urls import path,include
from api import views

app_name='api'

##defining the urls to work with

urlpatterns = [
    #path('members/',views.MemberList.as_view()),
    path('signup/',views.signupAppUser)
]
