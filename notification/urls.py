import imp
from django.urls import path,include
from notification import views

app_name='notification'


urlpatterns = [
    #landing_page
    path('',views.notification, name='all_notifications'),
    path('mark_as_read/',views.MarkNotificationAsReadAjax.as_view(), name='mark_as_read'),
    path('mark_as_unread/',views.MarkNotificationAsUnReadAjax.as_view(), name='mark_as_unread'),
    path('delete_notification_user/',views.DeleteNotifcationUserAjax.as_view(),name="delete_notification_user"),
]
