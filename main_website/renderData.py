from .models import HomePageTopBanner,BannerPictureWithStat
from django.http import HttpResponseServerError
from users.models import Members,User_IP_Address,Panel_Members
from membership_development_team.renderData import MDT_DATA
from central_events.models import Events,InterBranchCollaborations
from port.models import Chapters_Society_and_Affinity_Groups,Roles_and_Position,Panels
from graphics_team.models import Graphics_Banner_Image
from media_team.models import Media_Images
from datetime import datetime
import traceback
from system_administration.system_error_handling import ErrorHandling
import logging
from django.contrib import messages
from django.utils import timezone
from chapters_and_affinity_group.models import SC_AG_Members,SC_AG_FeedBack
from chapters_and_affinity_group.get_sc_ag_info import SC_AG_Info
from central_branch.renderData import Branch
class HomepageItems:

    logger=logging.getLogger(__name__)

    def load_all_events(request,flag,primary):

        ''' This function returns all the events with its banner picture depending on the value of flag being True or False'''
            
            #when flag is true we are trying to fetch all events, else latest five events
        
        try:
            #getting current date to compare with events date that are upcoming
            #current_datetime = timezone.now()
            #getting which societies event to load
            society = SC_AG_Info.get_sc_ag_details(request,primary)
            #declaring dictionart to store event object as key and graphic banner object as value
            dic = {}
            if flag:
                #when flag is true , checking to see if primary is 1 to get all events
                if primary == 1:
                    events = Events.objects.filter(publish_in_main_web= True,).order_by('-event_date') 
                else:
                    #when True getting all the events which are published, is of particular society and is ordered by latest date
                    events =  Events.objects.filter(publish_in_main_web= True,event_organiser = society).order_by('-event_date')
                    ####getting collaborated events###if dont want collaborated event remove bottom section
                    collaborations = InterBranchCollaborations.objects.filter(collaboration_with = society).values_list('event_id')
                    #joining both the events list of collbarated and their own organised events
                    events = events.union(Events.objects.filter(pk__in=collaborations,publish_in_main_web= True)).order_by('-event_date') 
                    ####################################################################################################################
            else:
                if primary == 1:
                    #when false getting latest five events
                    events = Events.objects.filter(publish_in_main_web= True).order_by('-event_date')[:5]
                else:
                    #when False getting events 5 events which are upcoming, is published and is of particular society
                    events = Events.objects.filter(publish_in_main_web= True,event_organiser = society).order_by('event_date')#[:5]
                    ####getting collaborated events###if dont want collaborated event remove bottom section and uncommment the list here -----------------------here
                    collaborations = InterBranchCollaborations.objects.filter(collaboration_with = society).values_list('event_id')
                    #joining both the events list of collbarated and their own organised events
                    events = events.union(Events.objects.filter(pk__in=collaborations,publish_in_main_web= True)).order_by('-event_date')[:5]
                    ####################################################################################################################

            #using this loop, assigning the event with its corresponding banner picture in the dictionary as key and value
            for i in events:
                #getting the event banner image using load_event_banner_image funtion
                event_selected_image = HomepageItems.load_event_banner_image(i.pk)
                if event_selected_image == None:
                    #else assigning '#'
                    dic[i] = "#"
                else:
                    #if not none assigning banner image as value to the event which is the key
                    dic[i]=event_selected_image
            return dic
        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    
    def load_event_banner_image(event_id):
            
        '''This function returns the banner_image for the particular event'''
        try:
            #getting the banner image using the event id sent as parameter
            return Graphics_Banner_Image.objects.get(event_id = event_id).selected_image
        except:
            #if not found any image returning none
            return None
    
    def load_event_gallery_images(event_id):

        '''This function loads all the media images for the particular event'''

        return Media_Images.objects.filter(event_id = event_id)

    
    def load_featured_events(sc_ag_primary):
        '''This function loads all the featured events for SC Ag & Branch with banners'''
        # get featured events
        featured_event=Events.objects.filter(event_organiser=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),is_featured=True).order_by('-event_date')[:6] 
        # store event data (event obj+ event banner obj in a dictionary) in a list
        featured_event_list=[]
        
        # create dictionary of featured events and then keep it on the list
        for i in featured_event:
            featured_event_dict={}
            # store event obj in 'featured_event' key
            featured_event_dict['featured_event']=i
            # get banner image of every event and put it into the 'banner_image" key
            featured_event_dict['banner_image']=HomepageItems.load_event_banner_image(event_id=i.pk)
            # store the dict in the list
            featured_event_list.append(featured_event_dict)
        
        return featured_event_list
        
        
    def getHomepageBannerItems():
        
        try:
            return HomePageTopBanner.objects.all().order_by('pk')
            
        except Exception as e:
            print(e)
            response = HttpResponseServerError("Oops! Something went wrong.")
            return response
    
    def getBannerPictureWithStat():

        try:
            getItem=BannerPictureWithStat.objects.first()
            return getItem.image
        except Exception as e:
            print(e)
            response = HttpResponseServerError("Oops! Something went wrong.")
            return response
        
    def getAllIEEEMemberCount():
        '''Gets all the count of members in Database'''
        return Members.objects.all().count()
    
    def getActiveMemberCount():
        '''Gets all the active Member count'''
        activeMemberCount=0
        
        allMembers=Members.objects.all()

        for i in allMembers:
            if(MDT_DATA.get_member_account_status(i.ieee_id)):
                activeMemberCount+=1

        return activeMemberCount
    
    def getEventCount():
        '''Gets all the event Count'''
        return Events.objects.all().count()

    def get_event_for_calender(request,primary):

        '''This function returns the events to show them on calender'''
        
        try:
            #getting all events according to the socities and affinity group primary value
            if primary == 1:
                all_events = Events.objects.filter(publish_in_main_web= True).order_by('-event_date')
            else:
                society = SC_AG_Info.get_sc_ag_details(request,primary)
                #getting collaborated events
                collaborations = InterBranchCollaborations.objects.filter(collaboration_with = society).values_list('event_id')
                events = Events.objects.filter(publish_in_main_web= True,event_organiser = society).order_by('-event_date')
                #joining both the events list of collbarated and their own organised events
                all_events = events.union(Events.objects.filter(pk__in=collaborations,publish_in_main_web= True)).order_by('-event_date')   
            #decalring empty dictionary for getting the event date and event
            #key is the date and event object is the value
            date_and_events = {}
            #iterating over each event
            for event in all_events:
                try:
                    #if date exists then formatting it
                    date = event.event_date.strftime("%Y-%m-%d")
                except:
                    #otherwise assigning empty value
                    date = ""
                #if date does not exist in dictionart then appending it
                if date in date_and_events:
                    date_and_events[date].append(event)
                #else not appending it
                else:
                    date_and_events[date] = [event]

            return date_and_events
        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    
    def get_upcoming_event(request,primary):

        '''This function returns a list of events which are upcoming'''
        
        try:
            current_datetime = timezone.now()
            society = SC_AG_Info.get_sc_ag_details(request,primary)
            if primary == 1:
                upcoming_event = Events.objects.filter(publish_in_main_web = True,event_date__gt=current_datetime).order_by('event_date')[:1]
            else:
                #getting the latest upcoming event for affinity groups and societies
                upcoming_event = Events.objects.filter(publish_in_main_web = True,event_date__gt=current_datetime,event_organiser = Chapters_Society_and_Affinity_Groups.objects.get(primary = primary)).order_by('event_date')#[:1]
                #getting collaborated upcoming event#if dont want this then remove bottom section and uncomment the list value to one, in the top line --------------------------------------------------------------------------here
                collaborations = InterBranchCollaborations.objects.filter(collaboration_with = society).values_list('event_id')
                #joining both the events list of collbarated and their own organised events
                upcoming_event = upcoming_event .union(Events.objects.filter(pk__in=collaborations,publish_in_main_web= True,event_date__gt=current_datetime)).order_by('event_date')[:1] 
                #########################################################################################################################################################################
            #returning only the first item of the list as filter always returns a list
            return upcoming_event[0]
        except:
            return None 
    
    def get_ip_address(request):

        '''This function saves the ip address every day. So if same user visits the page everyday,
            then each day his ip address will counted only once'''
        
        try:
            address = request.META.get('HTTP_X_FORWARDED_FOR')
            if address:
                ip = address.split(',')[-1].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')
            #creating user IP address model with auto saved date
            user =User_IP_Address(ip_address = ip)
            #checking if this user already exists today or not. If yes the length of result is more than 1
            #and his ip wont be saved
            result = User_IP_Address.objects.filter(ip_address = ip,created_at = datetime.today())
            if len(result)>=1:
                pass
            else:
                user.save()
        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False

    def get_featured_events_for_societies(primary):

        '''This funtion gets the featured events for the societies depending on primary value'''
        
        try:
            dic={}
            events = Events.objects.filter(event_organiser = Chapters_Society_and_Affinity_Groups.objects.get(primary = primary),is_featured = True,publish_in_main_web= True).order_by('-event_date')[:4]
            print(events)
            #iterating for each event to set graphics banner image
            for i in events:
                    #getting the event banner image using load_event_banner_image funtion
                    event = HomepageItems.load_event_banner_image(i.pk)
                    if event == None:
                        #else assigning '#'
                        dic[i] = "#"
                    else:
                        #if not none assigning banner image as value to the event which is the key
                        dic[i]=event
                        
            return dic
        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def get_faculty_advisor_for_society(request,primary):

        '''This function returns the faculty advisor for the particular society otherwise return none''' 
        
        try:
            
            try:
                #getting the particular society object
                society = Chapters_Society_and_Affinity_Groups.objects.get(primary=primary)
                #getting position
                position = Roles_and_Position.objects.get(is_faculty = True,role_of = society,is_sc_ag_eb_member = True)
                #getting current tenure
                current_tenure = Panels.objects.get(current = True, panel_of = society)
                #getting the faculty
                faculty = Panel_Members.objects.get(tenure = current_tenure,position =position)

            except:
                #else returning None
                faculty = None

            return faculty

        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def get_eb_members_for_society(request,primary):

        '''This function returns a list of eb memebers for the particular society'''
        
        try:
            try:
                #assingning empty eb_member list
                eb_members=[]
                #getting the particular society object
                society = Chapters_Society_and_Affinity_Groups.objects.get(primary=primary)
                #getting current tenure
                current_tenure = Panels.objects.get(current = True, panel_of = society)
                #getting all th eb roles
                roles = Roles_and_Position.objects.filter(is_sc_ag_eb_member = True,role_of = society,is_mentor = True).order_by('role_of','role')
                for role in roles:
                    try:
                        #getting the member of the particular society whose role matches with the role iteration in the list and is if current panel
                        member = Panel_Members.objects.get(tenure = current_tenure,position = role)
                        eb_members.append(member)
                    except:
                        pass
                return eb_members
            except:
                #returning empty list
                return eb_members
        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def save_feedback_information(request,primary,name,email,message):

        '''This function saves the feedback data to the database'''

        try:
            #getting the particular society object
            society = SC_AG_Info.get_sc_ag_details(request,primary)
            #creating the new feedback object for the particular society
            feedback = SC_AG_FeedBack.objects.create(society = society, name = name,email = email, message = message)
            #saving it to the database
            feedback.save()
            return True

        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False

    

        