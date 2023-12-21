from django.contrib import admin
from .models import Content_Team_Document,Content_Notes
# Register your models here.

@admin.register(Content_Team_Document)
class Content_Team_Document(admin.ModelAdmin):
    list_display = ['id','event_id','document']

@admin.register(Content_Notes)
class Content_Notes(admin.ModelAdmin):
    list_display = ['id','event_id','title','notes']