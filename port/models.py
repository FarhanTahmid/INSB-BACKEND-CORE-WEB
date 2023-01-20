from django.db import models

# Create your models here.
class Teams(models.Model):
    team_name=models.CharField(max_length=40,null=False,blank=False)
    
    def __str__(self) -> str:
        return self.team_name


class Chapters_Society_and_Affinity_Groups(models.Model):
    group_name=models.CharField(null=False,blank=False,max_length=150)

    class Meta:
        verbose_name="Chapters-Societies-Affinity Group"
    def __str__(self) -> str:
        return self.group_name    

class Roles_and_Position(models.Model):
    role=models.CharField(max_length=40,null=False,blank=False)
    
    class Meta:
        verbose_name='Registered positions'
    def __str__(self) -> str:
        return self.role