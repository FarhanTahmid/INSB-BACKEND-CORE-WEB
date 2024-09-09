from django.db import models
from users.models import Members
from django.core.files.storage import FileSystemStorage

# Create your models here.



class Manage_Team(models.Model):

    ieee_id = models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    manage_team_access = models.BooleanField(default=False,null=False,blank=False,verbose_name="Team Access")
    manage_email_access = models.BooleanField(default=False,null=False,blank=False,verbose_name="Email Access")

    class Meta:

        verbose_name = "Manage Team Access"

    def __str__(self):
        return str(self.ieee_id)
    
# class Email_Attachements(models.Model):
#     email_name = models.CharField(null=True,blank=True,max_length = 1000)
#     email_content=models.FileField(upload_to="Email_Attachments/",blank=True,null=True,default=None)

#     class Meta:

#         verbose_name = "Email Attachments"

#     def __str__(self):
#         return str(self.email_name)

# class Email_Draft(models.Model):
#     email_unique_id = models.CharField(null=False,blank=False,max_length=20)
#     subject = models.TextField(blank=True,null=True)
#     drafts = models.JSONField(null=True,blank=True,default=dict)
#     timestamp = models.DateTimeField(null=False,blank=False,auto_now_add=True)

#     class Meta:
#         verbose_name = "Email Draft"

#     def __str__(self):
#         return str(self.email_unique_id)