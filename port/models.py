from django.db import models

# Create your models here.
class Teams(models.Model):
    team_name=models.CharField(max_length=40,null=False,blank=False)
    primary=models.IntegerField(null=False,blank=False,default=0)
    
    def __str__(self) -> str:
        return self.team_name


class Chapters_Society_and_Affinity_Groups(models.Model):
    group_name=models.CharField(null=False,blank=False,max_length=150)
    primary=models.IntegerField(null=False,blank=False,default=0)

    class Meta:
        verbose_name="Chapters-Societies-Affinity Group"
    def __str__(self) -> str:
        return self.group_name    

class Roles_and_Position(models.Model):
    id=models.IntegerField(null=False,blank=False,default=0,primary_key=True)
    role=models.CharField(max_length=40,null=False,blank=False)
    is_eb_member = models.BooleanField(default=False)
    is_officer=models.BooleanField(default=False)
    is_faculty=models.BooleanField(default=False)
    
    class Meta:
        verbose_name='Registered positions'
    def __str__(self) -> str:
        return self.role