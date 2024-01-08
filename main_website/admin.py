from django.contrib import admin

from main_website.forms import About_IEEE_Bangladesh_Section_Form, About_IEEE_Form
from .models import Research_Papers,Blog_Category,Blog,IEEE_Bangladesh_Section,IEEE_Bangladesh_Section_Gallery,HomePage_Thoughts,About_IEEE,Page_Link
# Register your models here.
###Society AGS###
# RAS
from ieee_nsu_sb_ras_sbc.models import Ras_Sbc
@admin.register(Ras_Sbc)
class Ras_Sbc(admin.ModelAdmin):
    list_display=['id']

#Research Blogs Category
@admin.register(Research_Papers)
class ResearchPaper(admin.ModelAdmin):
    list_display = ['id','title','author_names','research_banner_picture','publication_link']
@admin.register(Blog_Category)
class Blog_Category(admin.ModelAdmin):
    list_display=['id','blog_category']
@admin.register(Blog)
class Blog(admin.ModelAdmin):
    list_display=['id','writer_name','title','date']
    

#Homepage Models
from . models import HomePageTopBanner
@admin.register(HomePageTopBanner)
class HomepageBannerData(admin.ModelAdmin):
    list_display=['id']

#Homepage Ribbon Picture
from . models import BannerPictureWithStat
@admin.register(BannerPictureWithStat)
class RibbonPicture(admin.ModelAdmin):
    list_display=['id']
    
# Achievements
from .models import Achievements
@admin.register(Achievements)
class Achievements(admin.ModelAdmin):
    list_display=['id','award_name','award_of']

from .models import Magazines
@admin.register(Magazines)
class Magazines(admin.ModelAdmin):
    list_display=['id','magazine_title']

@admin.register(IEEE_Bangladesh_Section)
class IEEE_Bangladesh_Section_Admin(admin.ModelAdmin):
    form=About_IEEE_Bangladesh_Section_Form
    list_display = ['id']  
    
@admin.register(IEEE_Bangladesh_Section_Gallery)
class IEEE_Bangldesh_Section_Gallery(admin.ModelAdmin):
    list_display=['picture']

@admin.register(About_IEEE)
class About_IEEE(admin.ModelAdmin):
    form=About_IEEE_Form
    list_display = ['id']

@admin.register(HomePage_Thoughts)
class HomePage_Thoughts(admin.ModelAdmin):

    list_display = ['quote','author']

from .models import GalleryImages
@admin.register(GalleryImages)
class GalleryImages(admin.ModelAdmin):
    list_display=['pk']

@admin.register(Page_Link)
class Page_Link(admin.ModelAdmin):
    list_display=['id', 'page_title', 'category', 'title', 'link']