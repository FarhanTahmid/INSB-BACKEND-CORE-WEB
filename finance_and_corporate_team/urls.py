from django.urls import path,include
from . import views

app_name="finance_and_corporate_team"

urlpatterns = [
    path('',views.team_homepage,name="team_homepage"),
    #Manage Team
    path('manage_team/',views.manage_team,name="manage_team")
]
