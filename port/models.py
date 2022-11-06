from django.db import models

# Create your models here.
class Teams(models.Model):
    team_name=models.CharField(max_length=40,null=False,blank=False)
    
    def __str__(self) -> str:
        return self.team_name