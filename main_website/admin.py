from django.contrib import admin
from .models import Research_Papers
# Register your models here.

@admin.register(Research_Papers)
class ResearchPaper(admin.ModelAdmin):
    list_display = ['id','title','author_names','research_banner_picture','publication_link']