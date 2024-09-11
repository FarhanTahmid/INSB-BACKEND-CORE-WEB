from django.db import models
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from central_events.models import Events
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

class Email_Draft(models.Model):
    email_unique_id = models.CharField(null=False,blank=False,max_length=20)
    subject = models.TextField(blank=True,null=True)
    drafts = models.JSONField(null=True,blank=True,default=dict)
    timestamp = models.DateTimeField(null=False,blank=False,auto_now_add=True)
    status = models.CharField(null=False,blank=False,choices=[('Scheduled','Scheduled'),('Sent','Sent'),('Paused','Paused'),('Failed','Failed'),('Unknown','Unknown')], default='Unknown',max_length=100)

    class Meta:
        verbose_name = "Email Draft"

    def __str__(self):
        return str(self.email_unique_id)