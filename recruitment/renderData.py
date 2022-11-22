#this file is solely responsible for collecting all the related data for recruitment site
from . models import recruitment_session,recruited_members

class Recruitment:
    id=''
    def __init__(self) -> None:
        pass
    def loadSession():
        '''Loads all the recruitment session present in the database'''
        return {'sessions':recruitment_session.objects.all().values()} #returns a dictionary which contains session dataa
    
    def getSession(session_id):
        """Returns the whole session object"""
        return{'session':recruitment_session.objects.get(id=session_id)} #returns the object who has got the id of passed session
    def getSessionid(session_name):
        """Returns the id of the session"""
        return{'session':recruitment_session.objects.filter(session=session_name).values('id')}
    def getRecruitedMembers(session_id):
        '''This function returns all the recruited members on that particular session'''
        return{
            'member': recruited_members.objects.filter(session_id=session_id).values()
        }
    
    def updateRecruiteeDetails(nsu_id,values):
        '''This function updates any changes happening to any recruitee'''    
        try:
            member=recruited_members.objects.get(nsu_id=nsu_id)
            print(values)
        except:
            pass
        
        
        
        
        
    def getRecruitedMemberDetails(nsu_id):
        '''This function extracts all the datas from the passes nsu_id'''
        return {'recruited_member':recruited_members.objects.filter(nsu_id=nsu_id).values('nsu_id',
                                                                                'first_name',                                                                                'middle_name','last_name',
                                                                                'contact_no',
                                                                                'date_of_birth',
                                                                                'email_personal',
                                                                                'gender',
                                                                                'facebook_url',
                                                                                'home_address',
                                                                                'major','graduating_year',
                                                                                'recruitment_time',
                                                                                'ieee_id',
                                                                                'session_id',
                                                                                'recruited_by',
                                                                                'cash_payment_status',
                                                                                'ieee_payment_status'
                                                                                )}
        
         