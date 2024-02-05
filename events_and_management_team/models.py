from django.db import models
from django.urls import reverse
from django.core.files.storage import FileSystemStorage





###### THIS BLOCK OF COODE IS FOR DECLARING DIRECTORIES TO STORE FILES#####
permission_template=FileSystemStorage(location='Permission-Templates')
event_proposal_template=FileSystemStorage(location='Template-Event-Proposal')
############################################################################






# Create your models here.


#list of the venues, primary key=id
class Venue_List(models.Model):
    venue_name=models.CharField(null=False,blank=True,max_length=50)
    
    class Meta:
        verbose_name="Venue"
    def __str__(self) -> str:
        return self.venue_name
    

#Permission Criterias For an event, primary key=id

class Permission_criteria(models.Model):
    permission_name=models.CharField(null=False,blank=False,max_length=50) 
    template=models.FileField(blank=True,null=True,storage=permission_template)
    class Meta:
        verbose_name="Permission Categories"
    def __str__(self) -> str:
        return self.permission_name
    def get_absolute_url(self):
        return reverse("permission_categories", kwargs={"permission_name": self.permission_name})


    

#Table for Event Proposal Templates

class Event_Proposal_Template(models.Model):
    event_name=models.CharField(max_length=50,null=False,blank=False)
    proposal_template=models.FileField(blank=True,null=True,storage=event_proposal_template)
    class Meta:
        verbose_name="Event Proposal Templates"
    def __str__(self) -> str:
        return self.event_name
    def get_absolute_url(self):
        return reverse("event_proposal_template", kwargs={"event_name": self.event_name})
    
