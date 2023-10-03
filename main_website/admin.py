from django.contrib import admin
from .models import Research_Papers,Blog_Category,Blog
# Register your models here.

#Research Blogs Category
@admin.register(Research_Papers)
class ResearchPaper(admin.ModelAdmin):
    list_display = ['id','title','author_names','research_banner_picture','publication_link']
@admin.register(Blog_Category)
class Blog_Category(admin.ModelAdmin):
    list_display=['id','blog_category']
@admin.register(Blog)
class Blog(admin.ModelAdmin):
    list_display=['id','title','date','blog_banner_picture','category','publisher','description','chapter_society_affinity']
    

#Homepage Models
from . models import HomepageBannerPictureWithText
@admin.register(HomepageBannerPictureWithText)
class HomepageBannerData(admin.ModelAdmin):
    list_display=['id']

#Homepage Ribbon Picture
from . models import BannerPictureWithStat
@admin.register(BannerPictureWithStat)
class RibbonPicture(admin.ModelAdmin):
    list_display=['id']