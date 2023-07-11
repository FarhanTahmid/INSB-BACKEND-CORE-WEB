from django.urls import path
from . import views

app_name = "main_website"

urlpatterns = [
    path('',views.index,name="main")
]
