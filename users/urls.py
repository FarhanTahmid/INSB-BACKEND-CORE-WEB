import imp
from django.urls import path,include
from . import views

app_name='users'

##defining the urls to work with

urlpatterns = [
    #include default auth urls
    #path('', include('django.contrib.auth.urls')),
    #loginpage
    path('login',views.login, name='login'),
    #dashboard
    path('dashboard',views.dashboard,name='dashboard'),
]
