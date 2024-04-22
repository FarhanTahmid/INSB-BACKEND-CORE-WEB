from django.urls import path,include
from django.contrib.auth.views import LogoutView
from . import views
from central_branch.views import upload_task


app_name='users'

##defining the urls to work with

urlpatterns = [
    #include default auth urls
    #path('', include('django.contrib.auth.urls')),
    #loginpage
    path('login',views.login, name='login'),
    # signup user validation
    path('signup/validation/',views.signup_user_validation,name="signup_validation"),
    #signup page
    path('signup/<int:ieee_id>/<str:token>/',views.signup,name='signup'),
    #dashboard
    path('dashboard',views.dashboard,name='dashboard'),
    #logoutUser
    path('logout/',views.logoutUser,name='logoutUser'),
    #user Profile
    path('profile',views.profile_page,name='profile'),
    #user Profile settings
    path('change_password',views.change_password,name='change_password'),
    #user Profile update information
    path('update_information',views.update_information,name='update_information'),
    #forgot password
    path('username_validation',views.forgotPassword_getUsername,name="fp_validation"), #fp=forgot password, this page just checks if the username is registered or not
    #forgot password
    path('reset_password/<str:username>/<str:token>/',views.forgotPassword_resetPassword,name="reset_password"),
    #Invalid URL Handling
    path('invalid_url',views.invalidURL,name="invalid_url"), #this page will prompt if an user has used an "used" or invalid url
    #my task url
    path('my_tasks/',views.my_tasks,name="my_tasks"),
    path('my_tasks/<int:task_id>',views.task_edit,name="task_edit"),
    path('my_tasks/<int:task_id>/upload_task/',upload_task,name="upload_task"),
 
]
