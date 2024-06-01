from django.db import models
from users.models import Members
# Create your models here.


class NotificationTypes(models.Model):
    
    '''This model stores all the types of notifications. Notification Types can be created from Branch Controls'''
    type=models.CharField(null=False,blank=False,max_length=100)
    
    class Meta:
        verbose_name="Notification Type"
    def __str__(self) -> str:
        return self.type
class Notifications(models.Model):
    
    '''This is the core model to store all the notifications.
        it stores:
            -type of the notification
            -timestamp of the notification created
            -general message of the notification. (basically it will be passed as a parameter,and will show on top)
            -inside link is the link user will be redirected to when clicked on a notification
            -created by stores the user id of the creator of the notification. basically takes the logged in ID the notification was created from
    '''
        
    type=models.ForeignKey(NotificationTypes,null=False,blank=False,on_delete=models.CASCADE)
    timestamp=models.DateTimeField(null=False,blank=False)
    general_message=models.CharField(null=True,blank=True,max_length=300)
    inside_link=models.URLField(null=False,blank=False)
    created_by=models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE)
    
    class Meta:
        verbose_name="Notification"
    def __str__(self) -> str:
        return str(self.pk)

class MemberNotifications(models.Model):
    
    '''This is an extension from Notifications. Every user has their own notification upon creation of notification.
        -it stores the original notification as foreign key
        -stores members to whom the notification is assigned
        -stores a boolean variable to check whether a notification is read or not.
    '''
    
    notification=models.ForeignKey(Notifications,null=False,blank=False,on_delete=models.CASCADE)
    member=models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE)
    is_read=models.BooleanField(null=False,blank=False,default=False)
    
    class Meta:
        verbose_name="Member Notifications"
    def __str__(self) -> str:
        return str(self.pk)