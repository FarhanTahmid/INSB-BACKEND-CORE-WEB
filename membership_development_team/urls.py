import imp
from django.urls import path,include
from . import views

app_name='users'

##defining the urls to work with

urlpatterns = [
   path('',views.md_team_homepage,name="md_team_homepage"),
]
