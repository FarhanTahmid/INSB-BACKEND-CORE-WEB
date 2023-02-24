import imp
from django.urls import path,include
from port import views

app_name='port'

##defining the urls to work with

urlpatterns = [
    #landing_page
    path('',views.homepage, name='homepage'),
    #developed by
    path('/developers',views.developed_by,name='developers')
]
