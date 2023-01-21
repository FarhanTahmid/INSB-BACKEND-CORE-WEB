from . models import Logistic_Item_List
class LogisticsTeam:
    
    def getLogisticsItem():
        return Logistic_Item_List.objects.all()