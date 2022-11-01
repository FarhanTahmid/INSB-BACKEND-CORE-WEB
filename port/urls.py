import imp
from django.urls import path,include
from . import views

app_name='port'

##defining the urls to work with

urlpatterns = [
    #include default auth urls
    #path('', include('django.contrib.auth.urls')),
    #loginpage
    path('',views.homepage, name='homepage'),
    
]
