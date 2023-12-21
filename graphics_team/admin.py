from django.contrib import admin
from .models import Graphics_Link,Graphics_Banner_Image,Graphics_Form_Link
# Register your models here.
@admin.register(Graphics_Link)
class Graphics_Link(admin.ModelAdmin):
    list_display = ['id','event_id','graphics_link']
@admin.register(Graphics_Banner_Image)
class Graphics_Banner_Image(admin.ModelAdmin):
    list_display=['id','event_id','selected_image']

@admin.register(Graphics_Form_Link)
class Graphics_Form_Link(admin.ModelAdmin):
    list_display=['event_id','graphics_form_link_name','graphics_form_link']