from django.db import models
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
# from events.models import Events
from port.models import Chapters_Society_and_Affinity_Groups
from logistics_and_operations_team.models import Logistic_Item_List
from events_and_management_team.models import Venue_List,Permission_criteria


# Create your models here.

###### THESE MODELS ARE SPECIFICALLY USED FOR EVENT HANDLING PURPOSE ####

###### THIS BLOCK OF COODE IS FOR DECLARING DIRECTORIES TO STORE FILES#####
event_proposal_files=FileSystemStorage(location='Event Proposals')
############################################################################


####### THIS BLOCK OF CODES REPRESENTS THE TABLES FOR SPECIFIC CREATED EVENTS #########


#Event type table
# class Event_type(models.Model):
#     event_type=models.CharField(null=False,blank=False,max_length=60)

#     class Meta:
#         verbose_name="Event Type"
#     def __str__(self) -> str:
#         return self.event_type
#     def get_absolute_url(self):
#         return reverse("event_type", kwargs={"pk": self.id})



#Table For Permissions for specific events
# class Event_Logistic_Items(models.Model):
#         event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
#         logistic_item_id=models.ForeignKey(Logistic_Item_List,null=True,blank=True,on_delete=models.CASCADE)
#         buying_status=models.BooleanField(null=False,blank=False,default=False)
#         spending_amount=models.FloatField(null=True,blank=True)
#         item_reciept=models.FileField(upload_to='Logistic Reciepts/',null=True,blank=True)


# #Table for Media Links and Images
# class Media_Links(models.Model):
#     event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
#     media_link=models.URLField(null=True,blank=True,max_length=300)
# class Media_Selected_Images(models.Model):
#     event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
#     selected_image=models.ImageField(upload_to='Event Selected Images/',null=True,blank=True,default=None)

# ######################################################################################    


# #Table for Graphics Links and Images
# class Graphics_Links(models.Model):
#     event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
#     graphics_link=models.URLField(null=True,blank=True,max_length=300)
# class Graphics_Files(models.Model):
#     event_id=models.ForeignKey(Events,on_delete=models.CASCADE)
#     graphics_file=models.FileField(null=True,blank=True,upload_to='Graphics Items/')
######################################################################################

# class meeting_minutes_team_info(models.Model):
#     mm_team_id=models.ForeignKey(team_meeting_minutes, on_delete=models.CASCADE)

#     class Meta:
#         verbose_name="Meeting Minutes Information of Teams"
#     def __str__(self) -> str:
#         return self.mm_team_id

# class meeting_minutes_branch_info(models.Model):
#     mm_branch_id=models.ForeignKey(branch_meeting_minutes, on_delete=models.CASCADE)

#     class Meta:
#         verbose_name="Meeting Minutes Information of Societies"
#     def __str__(self) -> str:
#         return self.mm_branch_id
