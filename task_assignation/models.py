import os
from django.db import models

from port.models import Chapters_Society_and_Affinity_Groups, Teams
from users.models import Members

# Create your models here.
class Task_Category(models.Model):
    name = models.TextField(null=False,blank=False)
    points = models.FloatField(null=False,blank=False)

    class Meta:
        verbose_name="Task Category"
    
    def __str__(self) -> str:
        return str(self.pk)

class Task(models.Model):
    title = models.TextField(null=False,blank=False)
    description = models.TextField(null=True,blank=True)
    task_category = models.ForeignKey(Task_Category,on_delete=models.CASCADE)
    task_type = models.CharField(null=False,blank=False,max_length=30,choices=(("Team","Team"),("Individuals","Individuals")))
    task_of = models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=False,blank=False,on_delete=models.CASCADE)
    task_created_by = models.CharField(null=False,blank=False,max_length=15)
    team = models.ManyToManyField(Teams,blank=True)
    members = models.ManyToManyField(Members,blank=True,related_name="members")
    start_date = models.DateTimeField(null=True,blank=True)
    deadline = models.DateTimeField(null=True,blank=True)
    others_description = models.TextField(null=True,blank=True)
    is_task_completed = models.BooleanField(null=False,blank=False,default=False)

    class Meta:
        verbose_name="Task"
        ordering = ['-deadline']
    
    def __str__(self) -> str:
        return str(self.pk)
    
class Member_Task_Upload_Types(models.Model):
    task_member = models.ForeignKey(Members, on_delete=models.CASCADE)
    task = models.ForeignKey(Task,null=False,blank=False,on_delete=models.CASCADE)
    has_drive_link = models.BooleanField(null=False,blank=False,default=False)
    has_file_upload = models.BooleanField(null=False,blank=False,default=False)
    has_content = models.BooleanField(null=False,blank=False,default=False)
    has_media = models.BooleanField(null=False,blank=False,default=False)
    has_permission_paper = models.BooleanField(null=False,blank=False,default=False)
    is_task_started_by_member = models.BooleanField(null=False,blank=False,default=False)

    class Meta:
        verbose_name="Member Task Upload Types"
    def __str__(self) -> str:
        return str(self.pk)

class Task_Drive_Link(models.Model):
    task = models.ForeignKey(Task,null=False,blank=False,on_delete=models.CASCADE)
    drive_link = models.URLField(null=True,blank=True)
    uploaded_by = models.CharField(max_length = 50,default = "")

    class Meta:
        verbose_name="Task Drive Link"

    def __str__(self) -> str:
        return str(self.pk)

class Task_Content(models.Model):
    task = models.ForeignKey(Task,null=False,blank=False,on_delete=models.CASCADE)
    content = models.TextField(null=True,blank=True)
    uploaded_by = models.CharField(max_length = 50,default = "")

    class Meta:
        verbose_name="Task Content"

    def __str__(self) -> str:
        return str(self.pk)
    
class Permission_Paper(models.Model):
    task = models.ForeignKey(Task,null=False,blank=False,on_delete=models.CASCADE)
    permission_paper = models.CharField(max_length=50,default = "")
    uploaded_by = models.CharField(max_length = 50,default = "")
    
class Task_Document(models.Model):
    task = models.ForeignKey(Task,null=False,blank=False,on_delete=models.CASCADE)
    document = models.FileField(null=True,blank=True,upload_to="Task_Assignation/Task_Documents/")
    uploaded_by = models.CharField(max_length = 50,default = "")

    class Meta:
        verbose_name="Task Document"

    def __str__(self) -> str:
        return str(self.pk)
    
    @property
    def filename(self) -> str:
        return os.path.basename(self.document.path)

class Task_Media(models.Model):
    task = models.ForeignKey(Task,null=False,blank=False,on_delete=models.CASCADE)
    media = models.ImageField(upload_to='Task_Assignation/Task_Media_Images/',null=True,blank=True)
    uploaded_by = models.CharField(max_length = 50,default = "")

    class Meta:
        verbose_name="Task Media"

    def __str__(self) -> str:
        return str(self.pk)
    
    @property
    def filename(self) -> str:
        return os.path.basename(self.media.path)
    
class Task_Log(models.Model):

    task_number = models.ForeignKey(Task,on_delete=models.CASCADE)
    task_log_details = models.JSONField()
    update_task_number = models.IntegerField(null=True,blank=True,default = 0)
    
    class Meta:
        verbose_name = "Task Log"

    def __str__(self) ->str:
        return self.task_number.title

class Member_Task_Point(models.Model):
    task = models.ForeignKey(Task,null=False,blank=False,on_delete=models.CASCADE)
    member = models.CharField(null=False,blank=False,max_length=15)
    completion_points = models.FloatField(null=False,blank=False,default=0)
    is_task_completed = models.BooleanField(null=False,blank=False,default=False)
    deducted_points_logs = models.JSONField(default = dict)
    comments = models.TextField(null=True,blank=True,default="")

    class Meta:
        verbose_name="Member Task Point"

    def __str__(self) -> str:
        return str(self.pk)
    
class Team_Task_Point(models.Model):
    task = models.ForeignKey(Task,null=False,blank=False,on_delete=models.CASCADE)
    team = models.ForeignKey(Teams,null=False,blank=False,on_delete=models.CASCADE)
    completion_points = models.FloatField(null=False,blank=False,default=0)
    is_task_completed = models.BooleanField(null=False,blank=False,default=False)

    class Meta:
        verbose_name="Team Task Point"

    def __str__(self) -> str:
        return str(self.pk)
    
class Team_Task_Forwarded(models.Model):

    task = models.ForeignKey(Task,null=False,blank=False,on_delete=models.CASCADE)
    team = models.ForeignKey(Teams,null=False,blank=False,on_delete=models.CASCADE)
    task_forwarded_to_incharge = models.BooleanField(default = False)
    task_forwarded_to_core_or_team_volunteers = models.BooleanField(default= False)
    forwared_by = models.CharField(null=False,blank=False,max_length=15,default="")
    forwarded_by_for_volunteers = models.CharField(null=False,blank=False,max_length=15,default="")

    class Meta:
        verbose_name="Team Task Forward"

    def __str__(self) -> str:
        return str(self.pk)