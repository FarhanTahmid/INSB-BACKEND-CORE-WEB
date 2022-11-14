#this file is solely responsible for collecting all the related data for recruitment site
from . models import recruitment_session,recruited_members
class Recruitment:
    def __init__(self) -> None:
        pass
    def loadSession():
        '''Loads all the recruitment session present in the database'''
        return {'sessions':recruitment_session.objects.all().values()} #returns a dictionary which contains session dataa
    def getSession(session_id):
        return{'session':recruitment_session.objects.get(id=session_id)} #returns the object who has got the id of passed session
    
    def getRecruitedMembers(session_id):
        return{
            'member': recruited_members.objects.filter(session_id=session_id).values()
        }    