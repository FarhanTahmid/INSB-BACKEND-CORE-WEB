from django.db import models

from port.models import Chapters_Society_and_Affinity_Groups, Teams
from users.models import Members

# Create your models here.
class Task_Category(models.Model):
    name = models.TextField(null=False,blank=False)
    points = models.IntegerField(null=False,blank=False)

    class Meta:
        verbose_name="Task Category"
    
    def __str__(self) -> str:
        return str(self.pk)

class Task(models.Model):
    title = models.TextField(null=False,blank=False)
    description = models.TextField(null=True,blank=True)
    task_category = models.ForeignKey(Task_Category, on_delete=models.CASCADE)
    task_type = models.CharField(null=False,blank=False,max_length=30,choices=(("Team","Team"),("Individuals","Individuals")))
    task_of = models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=False,blank=False,on_delete=models.CASCADE)
    team = models.ManyToManyField(Teams,blank=True)
    members = models.ManyToManyField(Members,blank=True)
    start_date = models.DateTimeField(null=True,blank=True)
    deadline = models.DateTimeField(null=True,blank=True)
    drive_link = models.TextField(null=True,blank=True)
    has_file_upload = models.BooleanField(null=False,blank=False,default=False)
    has_content = models.BooleanField(null=False,blank=False,default=False)
    has_picture_upload = models.BooleanField(null=False,blank=False,default=False)
    has_permission_paper = models.BooleanField(null=False,blank=False,default=False)
    is_task_completed = models.BooleanField(null=False,blank=False,default=False)

    class Meta:
        verbose_name="Task"
    
    def __str__(self) -> str:
        return str(self.pk)