from django.db import models
from django_resized import ResizedImageField
from ckeditor.fields import RichTextField
# Create your models here.

# RAS SBC
class Ras_Sbc(models.Model):
    ras_banner_image=ResizedImageField(upload_to='main_website_files/RAS/banner_picture')
    about_ras=RichTextField(null=False,blank=False,max_length=2000)
    mission_vision=RichTextField(null=False,blank=False,max_length=2000)
    mission_vision_picture=ResizedImageField(upload_to='main_website_files/RAS/mission_vision_picture')
    what_is_ras=RichTextField(null=True,blank=True,max_length=1000)
    why_join_ras=RichTextField(null=True,blank=True,max_length=1000)
    what_activities=RichTextField(null=True,blank=True,max_length=1000)
    how_to_join=RichTextField(null=True,blank=True,max_length=100)
    
    #RAS Contact Info
    address=models.CharField(null=True,blank=True,max_length=200)
    contact_no=models.CharField(null=True,blank=True,max_length=50)
    email=models.CharField(null=True,blank=True,max_length=100)
    
    class Meta:
        verbose_name="RAS SBC Informations"
    
    def __str__(self) -> str:
        return str(self.pk)

class Ras_Query_Form(models.Model):
    name=models.CharField(null=False,blank=False,max_length=100)
    email=models.EmailField(null=False,blank=False)
    message=models.CharField(null=False,blank=False,max_length=1000)
    
    class Meta:
        verbose_name="RAS SBC Contact Form Queries"
        
    def __str__(self) -> str:
        return str(self.pk)
