from django.db import models
from django.urls import reverse
from events_and_management_team.models import Permission_criteria, Venue_List
from django.core.files.storage import FileSystemStorage
from logistics_and_operations_team.models import Logistic_Item_List
from port.models import Chapters_Society_and_Affinity_Groups
from ckeditor.fields import RichTextField
from django_resized import ResizedImageField

# Create your models here.

###### THESE MODELS ARE SPECIFICALLY USED FOR EVENT HANDLING PURPOSE ####

###### THIS BLOCK OF COODE IS FOR DECLARING DIRECTORIES TO STORE FILES#####
event_proposal_files=FileSystemStorage(location='Event Proposals')
############################################################################


####### THIS BLOCK OF CODES REPRESENTS THE TABLES FOR SPECIFIC CREATED EVENTS #########

# Event Category Table
#Event categories are Group based.
class Event_Category(models.Model):
    event_category=models.CharField(null=False,blank=False,max_length=60)
    event_category_for = models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=True,blank=True,on_delete=models.CASCADE)
    # primary=models.IntegerField(null=False,blank=False)
    class Meta:
        verbose_name="Event Category"
    
    def __str__(self) -> str:
        return str(self.pk)
  

#Super event table. A super event is like IEEE Day events. Lots of events are done under this
#Super events primary key is the auto generated id
class SuperEvents(models.Model):
    mega_event_of=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=False,blank=False,on_delete=models.CASCADE,default=5)#Default is set to 5 to keep branch as default organizer of events
    super_event_name=models.CharField(null=False,blank=False,max_length=150)
    super_event_description=models.TextField(null=True,blank=True)
    start_date=models.DateField(null=True,blank=True,auto_now_add=False)
    end_date=models.DateField(null=True,blank=True,auto_now_add=False)
    banner_image=ResizedImageField(null=True,blank=True,upload_to='Mega_Event_Banner_Images/')
    publish_mega_event=models.BooleanField(null=False,blank=False,default=False)

    class Meta:
        verbose_name="Mega Event"
    def __str__(self) -> str:
        return str(self.pk)
    def get_absolute_url(self):
        return reverse("super_event", kwargs={"event_name": self.super_event_name})
    

#The events table. Primary key is the id
class Events(models.Model):
    event_name=models.CharField(null=False,blank=False,max_length=150)
    event_type=models.ManyToManyField(Event_Category,blank=True)
    super_event_id=models.ForeignKey(SuperEvents,null=True,blank=True,on_delete=models.CASCADE)
    event_description=RichTextField(null=True,blank=True)
    event_description_for_gc=RichTextField(null=True,blank=True)
    event_organiser=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=False,blank=False,on_delete=models.CASCADE,default=5)#Default is set to 5 to keep branch as default organizer of events, If a new database is created change this number according to the id of the branch
    event_date=models.DateField(null=True,blank=True,default = None)
    event_time=models.CharField(null=True,blank=True,max_length=100,default = None)
    registration_fee=models.BooleanField(null=False,blank=False,default=False)
    registration_fee_amount = models.TextField(blank=True, null=True,default = "Non-IEEE Member: 0 BDT\n\nIEEE Member: 0 BDT")
    flagship_event = models.BooleanField(null=False,blank=False,default=False)
    publish_in_main_web = models.BooleanField(null=False,blank=False,default=False)
    publish_in_google_calendar = models.BooleanField(null=False,blank=False,default=False)
    more_info_link = models.URLField(null=True,blank=True,max_length=500)
    form_link = models.URLField(null=True,blank=True,max_length=500)
    is_featured = models.BooleanField(null=False,blank=False,default=False,verbose_name="Feature this event")
    start_date = models.DateTimeField(null=True,blank=True)
    end_date = models.DateTimeField(null=True,blank=True)
    google_calendar_event_id = models.CharField(null=True,blank=True,max_length=100)


    class Meta:
        verbose_name="Registered Event"
    
    def __str__(self) -> str:
        return str(self.pk)
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

    class Meta:
        verbose_name="Event Permission"
    def __str__(self) -> str:
        return str(self.permission_id)

#Table For Permissions for specific events
class Event_Logistic_Items(models.Model):
        event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
        logistic_item_id=models.ForeignKey(Logistic_Item_List,null=True,blank=True,on_delete=models.CASCADE)
        buying_status=models.BooleanField(null=False,blank=False,default=False)
        spending_amount=models.FloatField(null=True,blank=True)
        item_reciept=models.FileField(upload_to='Logistic_Reciepts/',null=True,blank=True)

#Table for Media Links and Images
class Media_Links(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    media_link=models.URLField(null=True,blank=True,max_length=300)
class Media_Selected_Images(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    selected_image=models.ImageField(upload_to='Event_Selected_Images/',null=True,blank=True,default=None)

######################################################################################    


#Table for Graphics Links and Images
class Graphics_Links(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    graphics_link=models.URLField(null=True,blank=True,max_length=300)
class Graphics_Files(models.Model):
    event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
    graphics_file=models.FileField(null=True,blank=True,upload_to='Graphics_Items/')
######################################################################################
    
class Event_Feedback(models.Model):
    date = models.DateField(auto_now_add=True)
    event_id = models.ForeignKey(Events,null=False,blank=False,on_delete=models.CASCADE)
    name = models.CharField(null=False,blank=False,max_length=100)
    email = models.EmailField(null=False,blank=False)
    satisfaction = models.CharField(null=False,blank=False,max_length=50)
    comment = models.TextField(null=False,blank=False,max_length=400)

    class Meta:
        verbose_name="Event Feedback"
    def __str__(self) -> str:
        return str(self.pk)
    
class Google_Calendar_Attachments(models.Model):
    event_id = models.ForeignKey(Events,null=False,blank=False,on_delete=models.DO_NOTHING)
    file_id = models.CharField(null=False,blank=False,max_length=50)
    file_name = models.CharField(null=False,blank=False,max_length=100)
    file_url = models.CharField(null=False,blank=False,max_length=100)

    class Meta:
        verbose_name="Google Calendar Attachments"
    def __str__(self) -> str:
        return str(self.pk)