from django.db import models
from django.core.files.storage import FileSystemStorage
from port.models import Chapters_Society_and_Affinity_Groups
from django_resized import ResizedImageField
from PIL import Image

# Create your models here.

# Tables for Homepage
class HomepageBannerPictureWithText(models.Model):
    banner_picture=ResizedImageField(null=False,blank=False,upload_to='main_website_files/homepage/banner_pictures')
    first_layer_text=models.CharField(null=False,blank=False,default="FOCUSING LIMELIGHT ON",max_length=50)
    second_layer_text=models.CharField(null=False,blank=False,default="THE",max_length=20)
    second_layer_text_colored=models.CharField(null=False,blank=False,default="MASTERMINDS",max_length=20)
    third_layer_text=models.TextField(null=False,blank=False,max_length=500)
    button_text=models.CharField(null=False,blank=False,max_length=50,default="About INSB")
    button_url=models.CharField(null=False,blank=False,default="#",max_length=200)
    class Meta:
        verbose_name='Homepage Banner Picture With Texts'
    def __str__(self) -> str:
        return str(self.pk)

#Table for Ribbon Picture
class RibbonPicture(models.Model):

    image = models.ImageField(upload_to='main_website_files/homepage/ribbon_picture')

    def save(self, *args, **kwargs):
        # Open the uploaded image using Pillow
        img = Image.open(self.image.path)

        # Define your desired dimensions (width and height)
        desired_width = 1600  # Replace with your desired width
        desired_height = 450  # Replace with your desired height

        # Calculate the aspect ratio of the original image
        original_ratio = img.width / img.height

        # Calculate the desired aspect ratio
        desired_ratio = desired_width / desired_height

        # Check if the original image needs cropping
        if original_ratio != desired_ratio:
            if original_ratio > desired_ratio:
                # Crop the image horizontally to match the desired aspect ratio
                new_width = int(img.height * desired_ratio)
                left = (img.width - new_width) // 2
                top = 0
                right = left + new_width
                bottom = img.height
                img = img.crop((left, top, right, bottom))
            else:
                # Crop the image vertically to match the desired aspect ratio
                new_height = int(img.width / desired_ratio)
                left = 0
                top = (img.height - new_height) // 2
                right = img.width
                bottom = top + new_height
                img = img.crop((left, top, right, bottom))

        # Resize the image to the desired dimensions
        img = img.resize((desired_width, desired_height), Image.ANTIALIAS)

        # Save the modified image back to the same path
        img.save(self.image.path)

        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name="Ribbon Picture in Homepage"
    
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
