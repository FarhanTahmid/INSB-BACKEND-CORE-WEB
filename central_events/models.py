from django.db import models
from django.urls import reverse
from events_and_management_team.models import Permission_criteria, Venue_List
from django.core.files.storage import FileSystemStorage

from port.models import Chapters_Society_and_Affinity_Groups

# Create your models here.

###### THESE MODELS ARE SPECIFICALLY USED FOR EVENT HANDLING PURPOSE ####

###### THIS BLOCK OF COODE IS FOR DECLARING DIRECTORIES TO STORE FILES#####
event_proposal_files=FileSystemStorage(location='Event Proposals')
############################################################################


####### THIS BLOCK OF CODES REPRESENTS THE TABLES FOR SPECIFIC CREATED EVENTS #########

# Event Category Table
class Event_Category(models.Model):
    event_category=models.CharField(null=False,blank=False,max_length=60)
    
    class Meta:
        verbose_name="Event Category"
    
    def __str__(self) -> str:
        return str(self.pk)
  

#Super event table. A super event is like IEEE Day events. Lots of events are done under this
#Super events primary key is the auto generated id
class SuperEvents(models.Model):
    super_event_name=models.CharField(null=False,blank=False,max_length=150)
    super_event_description=models.CharField(null=True,blank=True,max_length=500)
    start_date=models.DateField(null=True,blank=True,auto_now_add=False)
    end_date=models.DateField(null=True,blank=True,auto_now_add=False)

    class Meta:
        verbose_name="Super Event"
    def __str__(self) -> str:
        return self.super_event_name
    def get_absolute_url(self):
        return reverse("super_event", kwargs={"event_name": self.super_event_name})
    

#The events table. Primary key is the id
class Events(models.Model):
    event_name=models.CharField(null=False,blank=False,max_length=150)
    # event_type=models.ForeignKey(Event_type,null=True,blank=True,on_delete=models.CASCADE)
    super_event_name=models.ForeignKey(SuperEvents,null=True,blank=True,on_delete=models.CASCADE)
    event_description=models.CharField(null=True,blank=True,max_length=1000)
    event_organiser=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=False,blank=False,on_delete=models.CASCADE,default=5)#Default is set to 5 to keep branch as default organizer of events, If a new database is created change this number according to the id of the branch
    event_date=models.DateField(null=True,blank=True)
    registration_fee=models.BooleanField(null=False,blank=False,default=False)
    flagship_event = models.BooleanField(null=False,blank=False,default=False)
    publish_in_main_web = models.BooleanField(null=False,blank=False,default=False)
    
    class Meta:
        verbose_name="Registered Event"
    
    def __str__(self) -> str:
        return self.event_name
    def get_absolute_url(self):
        return reverse("registered_events", kwargs={"event_name": self.event_name})

#Inter NSU Branch-Student Branch Collaboration   
class InterBranchCollaborations(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    collaboration_with=models.ForeignKey(Chapters_Society_and_Affinity_Groups,on_delete=models.CASCADE)
    
    class Meta:
        verbose_name="Inter Branch Collaborations"
    def __str__(self) -> str:
        return str(self.event_id)
    
    
#Collaboration Outside of NSU
class IntraBranchCollaborations(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    collaboration_with=models.CharField(null=True,blank=True,max_length=300) #max length kept long because there might be multiple collaborations

    class Meta:
        verbose_name="Intra Branch Collaborations"
    def __str__(self) -> str:
        return str(self.event_id)

#Table for event Proposal for specific events
class Event_Proposal(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    event_proposal=models.FileField(storage=event_proposal_files,blank=True,null=True,default=None)
    class Meta:
        verbose_name="Event Proposal"
    def __str__(self) -> str:
        return str(self.event_id)
    def get_absolute_url(self):
        return reverse("proposal", kwargs={"event_name": self.event_id})
    
# table for venues for specific events, One to Many Field, primary key will be auto incremented id    
class Event_Venue(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    venue_id=models.ForeignKey(Venue_List,on_delete=models.CASCADE)
    booking_status=models.BooleanField(null=False,blank=False,default=False)
    
    class Meta:
        verbose_name="Event Venue"
    def __str__(self) -> str:
        return str(self.venue_id)
    
#Table For Permissions for specific events
class Event_Permission(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    permission_id=models.ForeignKey(Permission_criteria,on_delete=models.CASCADE)
    permission_status=models.BooleanField(null=False,blank=False,default=False)