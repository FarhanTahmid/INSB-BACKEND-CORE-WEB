from django.urls import path,include
from django.contrib.auth.views import LogoutView
from . import views
from django.conf import settings

app_name='users'

##defining the urls to work with

urlpatterns = [
    #include default auth urls
    #path('', include('django.contrib.auth.urls')),
    #loginpage
    path('login',views.login, name='login'),
    #signup page
    path('signup',views.signup,name='signup'),
    #dashboard
    path('dashboard',views.dashboard,name='dashboard'),
    #logoutUser
    path('logout/',views.logoutUser,name='logoutUser'),
    #user Profile
    path('profile',views.profile_page,name='profile'),
    #forgot password
    path('username_validation',views.forgotPassword_getUsername,name="fp_validation") #fp=forgot password, this page just checks if the username is registered or not
    
]
