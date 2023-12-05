from django.db import models
from port.models import Chapters_Society_and_Affinity_Groups,Teams,Roles_and_Position
from users.models import Members
# Create your models here.

class SC_AG_Members(models.Model):
    sc_ag=models.ForeignKey(Chapters_Society_and_Affinity_Groups,null=False,blank=False,on_delete=models.CASCADE)
    member=models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE)
    team=models.ForeignKey(Teams,null=True,blank=True,on_delete=models.CASCADE)    
    position=models.ForeignKey(Roles_and_Position,null=True,blank=True,on_delete=models.CASCADE)
    
    class Meta:
        verbose_name="Society, Chapter & Affinity Group Member"
    
    def __str__(self) -> str:
        return str(self.member)
