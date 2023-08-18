from django.urls import path,include
from django.contrib.auth.views import LogoutView
from . import views
from django.conf import settings
from .Statistics import eventcountviews,eventtypeviews

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
    path('username_validation',views.forgotPassword_getUsername,name="fp_validation"), #fp=forgot password, this page just checks if the username is registered or not
    #forgot password
    path('reset_password/<str:username>/<str:token>/',views.forgotPassword_resetPassword,name="reset_password"),
    #Invalid URL Handling
    path('invalid_url',views.invalidURL,name="invalid_url"), #this page will prompt if an user has used an "used" or invalid url
    #GET STATISTIC URL
    path('get_dashboard_stats/',views.getDashboardStats,name="dashboard_stats"),
    #Get stat for mini chart 1
    path('get_dashboard_mini_chart1_stats/',eventcountviews.getDashboardMiniChart1Stats,name = "get_dashboard_mini_chart1_stats"),
    #Get stat for event type
    path('get_dashboard_event_type_stats/',eventtypeviews.getDashboardEventTypeStats,name="get_dashboard_event_type_stats")
]
