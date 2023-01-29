from django.db import models
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from port.models import Chapters_Society_and_Affinity_Groups
# Create your models here.

###### THESE MODELS ARE SPECIFICALLY USED FOR EVENT HANDLING PURPOSE ####

###### THIS BLOCK OF COODE IS FOR DECLARING DIRECTORIES TO STORE FILES#####
permission_template=FileSystemStorage(location='Permission Templates')
event_proposal_template=FileSystemStorage(location='Template-Event Proposal')
event_proposal_files=FileSystemStorage(location='Event Proposals')
############################################################################


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

#Table For Logistic Items , primary key=id
class Logistic_Item_List(models.Model):
    item_list=models.CharField(max_length=100,null=False,blank=False)
    class Meta:
        verbose_name="Logistic Item List"
    def __str__(self) -> str:
        return self.item_list
    def get_absolute_url(self):
        return reverse("logistic_item_list", kwargs={"item": self.item_list})
    

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
    

####### THIS BLOCK OF CODES REPRESENTS THE TABLES FOR SPECIFIC CREATED EVENTS #########

#Super event table. A super event is like IEEE Day events. Lots of events are done under this
#Super events primary key is the auto generated id
class SuperEvents(models.Model):
    super_event_name=models.CharField(null=False,blank=False,max_length=150)
    super_event_description=models.CharField(null=True,blank=True,max_length=500)
    start_date=models.DateField(null=True,blank=True,auto_now_add=False)
    end_date=models.DateField(null=True,blank=True,auto_now_add=False)

    class Meta:
        verbose_name="Mother Event"
    def __str__(self) -> str:
        return self.super_event_name
    def get_absolute_url(self):
        return reverse("super_event", kwargs={"event_name": self.super_event_name})
    

#The events table. Primary key is the id
class Events(models.Model):
    event_name=models.CharField(null=False,blank=False,max_length=150)
    super_event_name=models.ForeignKey(SuperEvents,null=True,blank=True,on_delete=models.CASCADE)
    event_description=models.CharField(null=True,blank=True,max_length=1000)
    event_organiser=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=False,blank=False,on_delete=models.CASCADE,default=5)#Default is set to 5 to keep branch as default organizer of events
    probable_date=models.DateField(null=True,blank=True,auto_now_add=False) #Must add probable date for an event
    final_date=models.DateField(null=True,blank=True,auto_now_add=False)
    registration_fee=models.BooleanField(null=False,blank=False,default=False)
    
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

#Table For Permissions for specific events
class Event_Logistic_Items(models.Model):
        event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
        logistic_id=models.ForeignKey(Logistic_Item_List,on_delete=models.CASCADE)
        buying_status=models.BooleanField(null=False,blank=False,default=False)
        item_reciept=models.FileField(upload_to='Logistic Reciepts/',null=True,blank=True)


#Table for Media Links and Images
class Media_Links(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    media_link=models.URLField(null=True,blank=True,max_length=300)
class Media_Selected_Images(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    selected_image=models.ImageField(upload_to='Event Selected Images/',null=True,blank=True,default=None)
    
#Table for Graphics Links and Images
class Graphics_Links(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    graphics_link=models.URLField(null=True,blank=True,max_length=300)
class Graphics_Files(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    graphics_file=models.FileField(null=True,blank=True,upload_to='Graphics Items/')
######################################################################################

