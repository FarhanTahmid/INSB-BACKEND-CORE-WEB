from django.db import models
from django.urls import reverse
# Create your models here.



#Table For Logistic Items , primary key=id
class Logistic_Item_List(models.Model):
    item_list=models.CharField(max_length=100,null=False,blank=False)
    class Meta:
        verbose_name="Logistic Item List"
    def __str__(self) -> str:
        return self.item_list
    def get_absolute_url(self):
        return reverse("logistic_item_list", kwargs={"item": self.item_list})