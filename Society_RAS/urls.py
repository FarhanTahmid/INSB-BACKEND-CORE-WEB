from django.urls import path,include
from . import views

app_name='Society_RAS'

##defining the urls to work with

urlpatterns = [
    #central_homeage
    path('',views.central_home, name='central_home'),
]
