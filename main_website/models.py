from django.db import models
from django.core.files.storage import FileSystemStorage
from port.models import Chapters_Society_and_Affinity_Groups
from django_resized import ResizedImageField
from PIL import Image
from ckeditor.fields import RichTextField
# Create your models here.
    
# Tables for Homepage
class HomePageTopBanner(models.Model):
    banner_picture=ResizedImageField(null=False,blank=False,upload_to='main_website_files/homepage/banner_pictures')
    first_layer_text=models.CharField(null=False,blank=False,default="FOCUSING LIMELIGHT ON",max_length=50)
    first_layer_text_colored=models.CharField(null=False,blank=False,default="MASTERMINDS",max_length=20)
    third_layer_text=models.TextField(null=False,blank=False,max_length=200)
    button_text=models.CharField(null=False,blank=False,max_length=50,default="About INSB")
    button_url=models.CharField(null=False,blank=False,default="#",max_length=200)
    class Meta:
        verbose_name='Homepage Banner Picture With Texts'
    def __str__(self) -> str:
        return str(self.pk)

#Table for Ribbon Picture
class BannerPictureWithStat(models.Model):

    image = ResizedImageField(upload_to='main_website_files/homepage/ribbon_picture')
    
    class Meta:
        verbose_name="Banner Picture with Statistics in Homepage"
    
    def __str__(self) -> str:
        return str(self.pk)

#Table for Research Papers
class Research_Papers(models.Model):
    title = models.CharField(null=False,blank=False,max_length=500)
    research_banner_picture = models.ImageField(null=False,blank=False,default='main_website/Research_pictures/default_research_banner_picture.png',upload_to='main_website/Research_pictures/')
    author_names = models.CharField(null=False,blank=False,max_length=1000)
    publication_link = models.URLField(null=False)

    class Meta:
        verbose_name = "Research Paper"
    def __str__(self):
        return f"{self.title} {self.author_names}"
    
#Table fot blog category
class Blog_Category(models.Model):
    blog_category = models.CharField(max_length=40,null=False,blank=False)

    def __str__(self):
        return self.blog_category
    
#Table for Blogs
class Blog(models.Model):
    title = models.CharField(null=False,blank=False,max_length=500)
    date = models.DateField()
    blog_banner_picture = models.ImageField(null=False,blank=False,default='main_website/Blog_banner_pictures/default_blog_banner_picture.png',upload_to='main_website/Blog_pictures/')
    category = models.ForeignKey(Blog_Category,null=True,blank=True,on_delete=models.CASCADE)
    publisher = models.CharField(null=False,blank=False,max_length=160)
    description = models.TextField(null=False,blank=False,max_length=5000,default="None")
    chapter_society_affinity = models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=True,blank=True,on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Blog"
    def __str__(self):
        return self.title

#Table for Achievements
class Achievements(models.Model):
    award_name=models.CharField(null=False,blank=False,max_length=100)
    award_description=RichTextField(null=True,blank=True,max_length=500)
    award_winning_year=models.IntegerField(null=False,blank=False)
    award_of=models.ForeignKey(Chapters_Society_and_Affinity_Groups,on_delete=models.CASCADE)
    award_picture=models.ImageField(null=False,blank=False,upload_to='main_website_files/achievements/')
    
    class Meta:
        verbose_name="Achievements"
    
    def __str__(self) -> str:
        return str(self.pk)
