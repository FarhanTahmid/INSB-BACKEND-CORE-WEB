import imp
from django.urls import path,include
from notification import views

app_name='notification'


urlpatterns = [
    #landing_page
    path('',views.notification, name='all_notifications')
]
