from django.db import models
from django.core.files.storage import FileSystemStorage
# Create your models here.

#Table for Research Papers
class Research_Papers(models.Model):
    title = models.CharField(null=False,blank=False,max_length=500)
    research_banner_picture = models.ImageField(null=True,blank=True,default='main_website/Research_pictures/default_research_banner_picture.png',upload_to='main_website/Research_pictures/')
    author_names = models.CharField(null=False,blank=False,max_length=1000)
    publication_link = models.URLField(null=False)

    class Meta:
        verbose_name = "Research Paper"
    def __str__(self):
        return f"{self.title} {self.author_names}"