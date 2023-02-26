
from django.urls import path,include
from . import views


app_name='public_relation_team'

urlpatterns = [
    path('',views.team_home_page,name='team_homepage'),
]
