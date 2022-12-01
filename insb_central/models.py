from django.db import models
from django.urls import reverse

# Create your models here.

###### THESE MODELS ARE SPECIFICALLY USED FOR EVENTS HANDLING PURPOSE ####

#The events table. Primary key is the id
class Events(models.Model):
    event_name=models.CharField(null=False,blank=False,max_length=150)
    event_description=models.CharField(null=True,blank=True,max_length=500)
    probable_date=models.DateField(null=True,blank=True,auto_now_add=False)
    collaboration_with=models.CharField(null=True,blank=True,max_length=100)
    final_date=models.DateField(null=True,blank=True,auto_now_add=False)
    class Meta:
        verbose_name="Registered Events"
    
    def __str__(self) -> str:
        return self.event_name
    def get_absolute_url(self):
        return reverse("registered_events", kwargs={"event_name": self.event_name})

#list of the venues, primary key=id
class Venue_List(models.Model):
    venue_name=models.CharField(null=False,blank=True,max_length=50)

#Permission Criterias For an event, primary key=id
class Permission_criteria(models.Model):
    permission_name=models.CharField(null=False,blank=False,max_length=50)    


# table for venues for specific events    
class Event_Venue(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    venue_id=models.ForeignKey(Venue_List,on_delete=models.CASCADE)

#table for event Proposal
class Event_Proposal(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    event_proposal=models.FileField(upload_to="event_proposals",blank=True,null=True,default=None)
    proposal_template=models.FileField(upload_to="event_proposals",blank=True,null=True,default=None)

#Table for Media Links and Images
class Media_Links(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    media_link=models.URLField(null=True,blank=True,max_length=300)
class Media_Selected_Images(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    selected_image=models.ImageField(upload_to="event_selected_pictures",null=True,blank=True,default=None)


