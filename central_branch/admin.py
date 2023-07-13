from django.contrib import admin
from . models import Events,SuperEvents,Event_type,Event_Venue,ResearchPaper,Blog,BlogCategory
# Register your models here.

#Creating customized View For DJANGO Admin
@admin.register(Event_type)
class Event_Type(admin.ModelAdmin):
    list_display=['id','event_type']
@admin.register(SuperEvents)
class Super_Events(admin.ModelAdmin):
    list_display=['super_event_name','start_date','end_date']
@admin.register(Events)
class Events(admin.ModelAdmin):
    list_display=['id','event_name','super_event_name','event_organiser','final_date','registration_fee','slug']
@admin.register(ResearchPaper)
class ResearchPaper(admin.ModelAdmin):
    list_display = ['id','Title','Author_names','Research_picture']
@admin.register(Blog)
class Blog(admin.ModelAdmin):
    list_display=('Title','Date','Category','Publisher','Society_Affinity','Description','Blog_picture')
@admin.register(BlogCategory)
class BlogCategory(admin.ModelAdmin):
    list_display=['blog_category',]
