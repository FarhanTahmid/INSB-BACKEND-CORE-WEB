from django.contrib import admin
from . models import Events
# Register your models here.

@admin.register(Events)
class Events(admin.ModelAdmin):
    list_display=['id','event_name','final_date']
