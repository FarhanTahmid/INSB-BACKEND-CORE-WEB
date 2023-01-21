from . models import Permission_criteria

class Events_And_Management_Team():

    def getPermissionCriterias():
        return Permission_criteria.objects.all()