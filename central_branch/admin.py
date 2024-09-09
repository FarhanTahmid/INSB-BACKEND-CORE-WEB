from django.contrib import admin
from .models import Email_Draft

# Register your models here.

#Creating customized View For DJANGO Admin
# @admin.register(Event_type)
# class Event_Type(admin.ModelAdmin):
#     list_display=['id','event_type']

@admin.register(Email_Draft)
class Email_Draft(admin.ModelAdmin):
    list_display = ['email_unique_id', 'subject', 'timestamp']
