from django.db import models
from users.models import Members

# Create your models here.

class PesMembers(models.Model):
    ieee_id=models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE)
    # position=models.ForeignKey(Society_Chapters_AG_Roles_and_Positions,null=False,blank=False,on_delete=models.CASCADE)
    # team=models.ForeignKey(Society_Chapters_AG_Teams,null=True,blank=True,on_delete=models.CASCADE)

    class Meta:
        verbose_name="PES Registered Members"
    
    def __str__(self) -> str:
        return str(self.ieee_id)