from django.db import models
from central_events.models import Events
from ckeditor.fields import RichTextField

# Create your models here.
class Content_Team_Document(models.Model):
    event_id = models.ForeignKey(Events,on_delete=models.CASCADE)
    document = models.FileField(blank=True,null=True,upload_to='Content_Team_Documents/')

    class Meta:
        verbose_name="Content Team Document"
    def __str__(self) -> str:
        return str(self.pk)
    
class Content_Team_Documents_Link(models.Model):
    event_id = models.ForeignKey(Events,on_delete=models.CASCADE)
    documents_link=models.URLField(null=True,blank=True,max_length=300)

    class Meta:
        verbose_name='Content Team Documents Link'
    def __str__(self) -> str:
        return str(self.pk)
    

class Content_Notes(models.Model):
    event_id = models.ForeignKey(Events,on_delete=models.CASCADE)
    title = models.CharField(null=True,blank=True,max_length=150)
    caption = RichTextField(null=True,blank=True)

    class Meta:
        verbose_name="Content Team Captions"
    def __str__(self) -> str:
        return str(self.pk)
    
class Content_Team_Content(models.Model):
    title = models.CharField(null=False,blank=False,max_length=150)
    description = RichTextField(null=True,blank=True)
    documents_link=models.URLField(null=True,blank=True,max_length=300)
    created_on=models.DateField(auto_now_add=True)

    class Meta:
        verbose_name="Content Team Content"
    def __str__(self) -> str:
        return str(self.pk)
    
class Content_Team_Content_Document(models.Model):
    document = models.FileField(blank=True,null=True,upload_to='Content_Team_Documents/')

    class Meta:
        verbose_name="Content Team Content Document"
    def __str__(self) -> str:
        return str(self.pk)

class Content_Team_Content_Caption(models.Model):
    title = models.CharField(null=True,blank=True,max_length=150)
    caption = RichTextField(null=True,blank=True)

    class Meta:
        verbose_name="Content Team Content Caption"
    def __str__(self) -> str:
        return str(self.pk)