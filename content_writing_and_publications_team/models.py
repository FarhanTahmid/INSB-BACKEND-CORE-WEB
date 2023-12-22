from django.db import models
from central_events.models import Events
from django.core.files.storage import FileSystemStorage
from ckeditor.fields import RichTextField


# Create your models here.
class Content_Team_Document(models.Model):
    event_id = models.ForeignKey(Events,on_delete=models.CASCADE)
    document = models.FileField(blank=True,null=True,upload_to='Content Team Documents/')

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
    notes = RichTextField(null=True,blank=True)

    class Meta:
        verbose_name="Content Team Notes"
    def __str__(self) -> str:
        return str(self.pk)

