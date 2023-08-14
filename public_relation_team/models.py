from django.db import models
from users.models import Members

# Create your models here.

class Manage_Team(models.Model):

    ieee_id = models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE,verbose_name="IEEE ID")
    manage_team_access = models.BooleanField(default=False,null=False,blank=False,verbose_name="Access")

    class Meta:

        verbose_name = "Manage Team Access"

    def __str__(self):
        return str(self.ieee_id)
