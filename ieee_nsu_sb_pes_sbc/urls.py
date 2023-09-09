from django.urls import path
from . import views

app_name="ieee_nsu_sb_pes_sbc"

#Defining urls for PES
urlpatterns = [
    # PES Homepage
    path('',views.pes_homepage,name='pes_homepage'),
    path('pes_members',views.pes_members,name='pes_members'),
]