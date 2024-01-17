#this file is solely responsible for collecting all the related data for recruitment site

from . models import recruitment_session,recruited_members
from django.db import IntegrityError
from django.db import InternalError
from django.core.exceptions import ObjectDoesNotExist
import random,string

from users.models import Members

class Recruitment:
    
    def __init__(self) -> None:
        pass
    
    
    
    def loadSession():
        '''Loads all the recruitment session present in the database'''
        return recruitment_session.objects.all().order_by('-id')
    
    
    
    def getSession(session_id):
        """Returns the name of the session"""
        return{'session':recruitment_session.objects.get(id=session_id)} #returns the object who has got the id of passed session
    
    
    
    def getSessionid(session_id):
        """Returns the session"""
        print(session_id)
        return recruitment_session.objects.get(id=session_id)
    
    
    
    def getRecruitedMembers(session_id):
        '''This function returns all the recruited members on that particular session'''
        return{
            'member': recruited_members.objects.filter(session_id=session_id).order_by('recruitment_time').values()
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
            member.emergency_contact_no=values['emergency_contact_no']
            member.date_of_birth = values['date_of_birth']
            member.email_personal = values['email_personal']
            member.email_nsu=values['email_nsu']
            member.facebook_url = values['facebook_url']
            member.facebook_username=values['facebook_username']
            member.home_address = values['home_address']
            member.major = values['major']
            member.graduating_year = values['graduating_year']
            member.recruited_by = values['recruited_by']
            member.cash_payment_status = values['cash_payment_status']
            member.ieee_payment_status = values['ieee_payment_status']
            member.comment=values['comment']
            if member.ieee_payment_status and member.ieee_id == "":
                return "no_ieee_id" #This is implied to enforce entering of ieee id upon completion of payment
            else:
                member.save() #Updating member data
                return True
        except IntegrityError:
            return IntegrityError
        
        
        
    
    def getRecruitedMemberDetails(nsu_id,session_id):
        '''This function extracts all the datas from the passes nsu_id'''
        try:
            return recruited_members.objects.get(nsu_id=nsu_id,session_id=session_id)
        except recruited_members.DoesNotExist:
            return False
    
    
    def deleteMember(nsu_id,session_id):
        '''
        This method is used to delete a member from the recruitment process
        this also checks if the member is registered in the main database or not and if yes,
        it deletes the member from there also
        '''
        try:
            #Gets member from the database
            deleteMember=recruited_members.objects.filter(nsu_id=nsu_id,session_id=session_id)
            deleteMember.delete()
            return True
            # #checks if the member is already registered in the main member database
            # if(Members.objects.filter(nsu_id=deleteMember.nsu_id).exists()):
            #     #deleting members from both database
            #     deleteMember2=Members.objects.get(ieee_id=deleteMember.ieee_id)
            #     deleteMember.delete()
            #     deleteMember2.delete()
            #     return "both_database" #Returns that it was deleted from both databases
            # elif (Members.objects.filter(nsu_id=deleteMember.nsu_id).exists()==False):
            #     #deleting member from recruitment process
            #     deleteMember.delete()
            #     return True
        except:
            return ObjectDoesNotExist


    def getTotalNumberOfMembers(session_id):
        return recruited_members.objects.filter(session_id=session_id).count()
    
    def getTotalCountofIEEE_payment_complete(session_id):
        return recruited_members.objects.filter(session_id=session_id,ieee_payment_status=True).count()
    
    def getTotalCountofIEEE_payment_incomplete(session_id):
        return recruited_members.objects.filter(session_id=session_id,ieee_payment_status=False).count()
    
    def generateUniqueCode(request,session,nsu_id):
        try:
            nsu_id=str(nsu_id)
            get_session=recruitment_session.objects.get(id=session)
            session_code='0'
            if('Spring' in get_session.session):
                session_code='1'
            elif('Summer' in get_session.session):
                session_code='2'
            elif('Fall' in get_session.session):
                session_code='3'
            
            session_unique_code=session_code+(get_session.session[-4:])
            nsu_id_code=nsu_id[3:7]
            security_code=Recruitment.generate_random_string(length=4)
            unique_code=nsu_id_code+security_code+session_unique_code
            return unique_code
            
        except Exception as e:
            print(e)

    def generate_random_string(length=4):
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string
