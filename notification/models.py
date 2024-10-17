from django.db import models
from users.models import Members
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from central_events.models import Events
from datetime import datetime

# Create your models here.


class NotificationTypes(models.Model):
    
    '''This model stores all the types of notifications. Notification Types can be created from Branch Controls'''
    type=models.CharField(null=False,blank=False,max_length=100)
    type_icon=models.ImageField(null=True,blank=True,upload_to='notification_icons/')
    
    class Meta:
        verbose_name="Notification Type"
    def __str__(self) -> str:
        return self.type
class Notifications(models.Model):
    
    '''This is the core model to store all the notifications. It stores:\n
            -`type` of the notification\n
            -`notification_of` It is used to link any model(for which the notification was triggered) with the notification.\n
            -`content_type` stores any model as notification_of's content_type(model) and is set automatically based on notification_of\n
            -`object_id` stores the foreign key value of notification_of and is set automatically. Is is used to search notifications\n
            -`timestamp` of the notification created\n
            -`general_message` of the notification. (basically it will be passed as a parameter,and will show on top)\n
            -`inside_link` is the link user will be redirected to when clicked on a notification\n
            -`created_by` stores the user id of the creator of the notification. basically takes the logged in ID the notification was created from
    '''
        
    type=models.ForeignKey(NotificationTypes,null=False,blank=False,on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,null=True,blank=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True,blank=True)
    notification_of=GenericForeignKey("content_type", "object_id")
    timestamp=models.DateTimeField(null=False,blank=False)
    title = models.CharField(null=True,blank=True,max_length=300)
    general_message=models.CharField(null=True,blank=True,max_length=50000)
    inside_link=models.URLField(null=False,blank=False)
    created_by=models.ForeignKey(Members,null=True,blank=True,on_delete=models.CASCADE)
    event = models.ForeignKey(Events,null=True,blank=True,default=None,on_delete=models.CASCADE)
    
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
    
class PushNotification(models.Model):

    '''This model will hold all the fcm token of users'''

    member=models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE)
    fcm_token=models.CharField(null=False,blank=False,max_length=1000)
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default = datetime.now)

    class Meta:
        verbose_name="Push Notification Tokens"
    def __str__(self) -> str:
        return str(self.pk)
