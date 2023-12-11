from django.contrib import admin
from .models import Event_Category,SuperEvents,Events,InterBranchCollaborations,IntraBranchCollaborations,Media_Links,Media_Selected_Images,Event_Venue,Event_Permission
# Register your models here.

@admin.register(Event_Category)
class Event_Category(admin.ModelAdmin):
    list_display = ['id','event_category','event_category_for']
@admin.register(SuperEvents)
class Super_Events(admin.ModelAdmin):
    list_display = ['super_event_name','super_event_description','start_date','end_date']

@admin.register(Events)
class Events(admin.ModelAdmin):
    list_display = ['id','event_name','event_types','super_event_id','event_organiser','event_date','registration_fee','registration_fee_amount','flagship_event','publish_in_main_web','form_link']

    def event_types(self, obj):
        return ", ".join([p.event_category for p in obj.event_type.all()])


@admin.register(InterBranchCollaborations)
class InterBranchCollaborations(admin.ModelAdmin):
    list_display=['id','event_id','collaboration_with']

@admin.register(IntraBranchCollaborations)
class IntraBranchCollaborations(admin.ModelAdmin):
    list_display=['id','event_id','collaboration_with']

@admin.register(Media_Links)
class Media_Links(admin.ModelAdmin):
    list_display=['event_id','media_link']

@admin.register(Media_Selected_Images)
class Media_Links(admin.ModelAdmin):
    list_display=['event_id','selected_image']

@admin.register(Event_Venue)
class Event_Venue(admin.ModelAdmin):
    list_display=['event_id','venue_id','booking_status']

@admin.register(Event_Permission)
class Event_Permission(admin.ModelAdmin):
    list_display=['event_id','permission_id','permission_status']