from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(NotificationTypes)
class NotificationTypes(admin.ModelAdmin):
    list_display=['pk','type']

@admin.register(Notifications)
class Notifications(admin.ModelAdmin):
    list_display=[
         'pk','type','created_by','general_message','timestamp'
    ]
    
@admin.register(MemberNotifications)
class MemberNotifications(admin.ModelAdmin):
    list_display=['notification','member','is_read']