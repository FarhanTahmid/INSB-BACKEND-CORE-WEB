from django.contrib import admin
from . models import Renewal_Sessions,Renewal_requests,Portal_Joining_Requests,Renewal_Form_Info
# Register your models here.
@admin.register(Renewal_Sessions)
class Renewal_Sessions(admin.ModelAdmin):
    list_display=['id','session_name','session_time']
@admin.register(Renewal_requests)
class Renewal_Requests(admin.ModelAdmin):
    list_display=['id','session_id_id','name']
@admin.register(Portal_Joining_Requests)
class Joining_Requests(admin.ModelAdmin):
    list_display=['ieee_id','name','position','team']
@admin.register(Renewal_Form_Info)
class Renewal_Form_Info(admin.ModelAdmin):
    list_display=['id','form_description']