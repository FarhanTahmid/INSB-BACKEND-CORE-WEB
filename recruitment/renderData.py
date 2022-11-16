#this file is solely responsible for collecting all the related data for recruitment site
from . models import recruitment_session,recruited_members
class Recruitment:
    id=''
    def __init__(self) -> None:
        pass
    def loadSession():
        '''Loads all the recruitment session present in the database'''
        return {'sessions':recruitment_session.objects.all().values()} #returns a dictionary which contains session dataa
    def set_session(session_id):
        id=session_id
    def return_session():
        return id
    def getSession(session_id):
        """Returns the whole session object"""
        return{'session':recruitment_session.objects.get(id=session_id)} #returns the object who has got the id of passed session
    
    def getRecruitedMembers(session_id):
        '''This function returns all the recruited members on that particular session'''
        return{
            'member': recruited_members.objects.filter(session_id=session_id).values()
        }
    def getRecruitedMemberDetails(nsu_id):
        '''This function extracts all the datas from the passes nsu_id'''
        pass    