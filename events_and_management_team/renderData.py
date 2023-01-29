from . models import Permission_criteria,Venue_List

class Events_And_Management_Team():

    def getPermissionCriterias():
        '''This method loads all the permission criterias needed for an event'''
        
        return Permission_criteria.objects.all()
    
    def getVenues():
        '''This method loads all the venues from the database'''
        return Venue_List.objects.all()