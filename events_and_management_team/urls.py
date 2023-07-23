from django.urls import path,include
from . import views

app_name='events_and_management_team'

urlpatterns = [
    path('',views.em_team_homepage,name="em_team_homepage"),
    path('data_access/',views.data_access,name="data_access")
]
