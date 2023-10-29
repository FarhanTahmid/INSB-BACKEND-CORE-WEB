from django.urls import path,include
from django.contrib.auth.views import LogoutView
from . import views
from django.conf import settings

app_name='system_administration'

urlpatterns = [
    path('',views.main_website_update_view,name="main_web_update")
]
