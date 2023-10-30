from django.db import models
from users.models import Members
from port.models import Teams,Roles_and_Position
# Create your models here.

# Membership Table for PES Members
class PesMembers(models.Model):
    ieee_id=models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE)
    position=models.ForeignKey(Roles_and_Position,null=True,blank=True,on_delete=models.CASCADE)
    team=models.ForeignKey(Teams,null=True,blank=True,on_delete=models.CASCADE)

    class Meta:
        verbose_name="PES Registered Members"
    
    def __str__(self) -> str:
        return str(self.ieee_id)
    

# Data Access table for PES
class PesDataAccess(models.Model):
    ieee_id=models.ForeignKey(Members,null=False,blank=False,on_delete=models.CASCADE)
    renewal_data_access=models.BooleanField(null=False,blank=False,default=False)
    
    class Meta:
        verbose_name="PES Data Access"
    def __str__(self) -> str:
        return str(self.ieee_id)