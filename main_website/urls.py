from django.urls import path
from . import views

app_name = "main_website"

urlpatterns = [
    path('',views.index,name="main"),
    path('all-events/',views.All_Events,name='all-events'),
    path('events/<slug:event_name>',views.Event_Details,name='event-details'),
    path('research-papers/',views.Research_Paper,name="research_papers"),
    path('blogs/',views.Blogs,name="blogs"),
    path('blogs/<slug:blog_title>',views.blog_Description,name="blog_Description")
    
]
