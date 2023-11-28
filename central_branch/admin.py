from django.contrib import admin
<<<<<<< HEAD
from . models import Events,SuperEvents,Event_Venue,InterBranchCollaborations,IntraBranchCollaborations,Media_Links,Media_Selected_Images
# Register your models here.

#Creating customized View For DJANGO Admin
# @admin.register(Event_type)
# class Event_Type(admin.ModelAdmin):
#     list_display=['id','event_type']
=======
from . models import Events,SuperEvents,Event_Venue,InterBranchCollaborations,IntraBranchCollaborations,Media_Links,Media_Selected_Images,Type_of_Event
# Register your models here.

#Creating customized View For DJANGO Admin

@admin.register(Type_of_Event)
class Type_of_Event(admin.ModelAdmin):
    list_display=['id','type_of_event']
>>>>>>> ed91f36dbc8598f877ad6cfcd7356c4d0f79cb8b
@admin.register(SuperEvents)
class Super_Events(admin.ModelAdmin):
    list_display=['super_event_name','start_date','end_date']
@admin.register(Events)
class Events(admin.ModelAdmin):
<<<<<<< HEAD
    list_display=['id','event_name','super_event_name','event_organiser','event_date','registration_fee','flagship_event','publish_in_main_web']
=======
    list_display=['id','event_name','super_event_name','type_of_event','event_organiser','event_date','registration_fee','flagship_event','publish_in_main_web']
>>>>>>> ed91f36dbc8598f877ad6cfcd7356c4d0f79cb8b

@admin.register(InterBranchCollaborations)
class InterBranchCollaborations(admin.ModelAdmin):
    list_display=['id','event_id','collaboration_with']

@admin.register(IntraBranchCollaborations)
class IntraBranchCollaborations(admin.ModelAdmin):
    list_display=['event_id','collaboration_with']
@admin.register(Media_Links)
class Media_Links(admin.ModelAdmin):
    list_display=['event_id','media_link']
@admin.register(Media_Selected_Images)
class Media_Links(admin.ModelAdmin):
    list_display=['event_id','selected_image']


