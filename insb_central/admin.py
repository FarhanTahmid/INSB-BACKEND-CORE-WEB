from django.contrib import admin
from . models import Events,Permission_criteria,SuperEvents,Venue_List,Logistic_Item_List
# Register your models here.

#Creating customized View For DJANGO Admin
@admin.register(SuperEvents)
class Super_Events(admin.ModelAdmin):
    list_display=['super_event_name','start_date','end_date']
@admin.register(Events)
class Events(admin.ModelAdmin):
    list_display=['id','event_name','super_event_name','event_organiser','final_date','registration_fee'] 


@admin.register(Venue_List)
class Venue(admin.ModelAdmin):
    list_display=['id','venue_name']

@admin.register(Permission_criteria)
class Permission_Category(admin.ModelAdmin):
    list_display=['id','permission_name','template']

@admin.register(Logistic_Item_List)
class Logistic_Item(admin.ModelAdmin):
    list_display=['id']