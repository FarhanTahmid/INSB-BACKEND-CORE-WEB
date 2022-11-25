#this file is solely responsible for collecting all the related data for recruitment site
from pymysql import NULL
from . models import recruitment_session,recruited_members
from django.db import IntegrityError
from django.db import InternalError
from users.models import Members

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
            member = recruited_members.objects.get(nsu_id=nsu_id)
            member.ieee_id = values['ieee_id']
            member.first_name = values['first_name']
            member.middle_name = values['middle_name']
            member.last_name = values['last_name']
            member.contact_no = values['contact_no']
            member.date_of_birth = values['date_of_birth']
            member.email_personal = values['email_personal']
            member.facebook_url = values['facebook_url']
            member.home_address = values['home_address']
            member.major = values['major']
            member.graduating_year = values['graduating_year']
            member.recruited_by = values['recruited_by']
            member.cash_payment_status = values['cash_payment_status']
            member.ieee_payment_status = values['ieee_payment_status']
            if member.ieee_payment_status and member.ieee_id == "":
                return "no_ieee_id"
            else:
                member.save()
                # Registering member to the main database
                if member.ieee_payment_status and member.ieee_id != '':
                    if (Members.objects.filter(ieee_id=member.ieee_id).exists()):
                        return "already_registered"
                    else:
                        newMember = Members(
                        ieee_id=int(values['ieee_id']),
                        name=member.first_name + " "+member.middle_name+" " + member.last_name,
                        nsu_id=member.nsu_id,
                        email_personal=member.email_personal,
                        contact_no=member.contact_no,
                        home_address=member.home_address,
                        date_of_birth=member.date_of_birth,
                        gender=recruited_members.objects.filter(
                        nsu_id=nsu_id).values('gender'),
                        facebook_url=member.facebook_url,
                        session=recruited_members.objects.filter(
                            nsu_id=nsu_id).values('session_id'),
                        )
                        newMember.save()
                    return "success"
        except IntegrityError:
            return IntegrityError
        except:
            return InternalError
        
        
        
        
        
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
        
         