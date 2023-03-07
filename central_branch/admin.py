from django.contrib import admin
from . models import Events,SuperEvents
# Register your models here.

#Creating customized View For DJANGO Admin
# @admin.register(SuperEvents)
# class Eve(admin.ModelAdmin):
#     list_display=['super_event_name','start_date','end_date']
@admin.register(SuperEvents)
class Super_Events(admin.ModelAdmin):
    list_display=['super_event_name','start_date','end_date']
@admin.register(Events)
class Events(admin.ModelAdmin):
    list_display=['id','event_name','super_event_name','event_organiser','final_date','registration_fee'] 

