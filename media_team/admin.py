from django.contrib import admin
from .models import Media_Link,Media_Images

# Register your models here.
@admin.register(Media_Link)
class Media_Link(admin.ModelAdmin):
    list_display = ['id','event_id','media_link','logo_link']
@admin.register(Media_Images)
class Media_Images(admin.ModelAdmin):
    list_display=['id','event_id','selected_images']