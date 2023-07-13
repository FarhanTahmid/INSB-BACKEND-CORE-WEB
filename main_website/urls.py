from django.urls import path
from . import views

app_name = "main_website"

urlpatterns = [
    path('',views.index,name="main"),
    path('all-events/',views.All_Events,name='all-events'),
    path('events/<slug:event_name>',views.Event_Details,name='event-details'),
    path('research-papers/',views.Research_Paper,name="research_papers")
]
