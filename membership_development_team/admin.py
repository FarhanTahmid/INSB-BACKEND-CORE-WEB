from django.contrib import admin
from . models import Renewal_Sessions,Renewal_requests,Portal_Joining_Requests
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