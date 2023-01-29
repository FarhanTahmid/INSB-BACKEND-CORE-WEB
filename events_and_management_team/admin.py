from django.contrib import admin
from . models import Venue_List,Permission_criteria
# Register your models here.
@admin.register(Venue_List)
class Venue(admin.ModelAdmin):
    list_display=['id','venue_name']

@admin.register(Permission_criteria)
class Permission_Category(admin.ModelAdmin):
    list_display=['id','permission_name','template']