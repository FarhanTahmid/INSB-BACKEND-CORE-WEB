from django.db import models

# Create your models here.
class Teams(models.Model):
    team_name=models.CharField(max_length=40,null=False,blank=False)
    
    def __str__(self) -> str:
        return self.team_name
class Roles_and_Position(models.Model):
    role=models.CharField(max_length=40,null=False,blank=False)
    
    class Meta:
        verbose_name='Registered positions'
    def __str__(self) -> str:
        return self.role