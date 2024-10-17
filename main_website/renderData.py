from .models import HomePageTopBanner,BannerPictureWithStat,Achievements
from django.http import HttpResponseServerError
from users.models import Members,User_IP_Address,Panel_Members
from membership_development_team.renderData import MDT_DATA
from central_events.models import Events,InterBranchCollaborations,SuperEvents
from port.models import Chapters_Society_and_Affinity_Groups,Roles_and_Position,Panels, Teams
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
                    events = Events.objects.filter(publish_in_main_web= True,).order_by('-start_date','-event_date') 
                else:
                    #when True getting all the events which are published, is of particular society and is ordered by latest date
                    events =  Events.objects.filter(publish_in_main_web= True,event_organiser = society).order_by('-start_date','-event_date')
                    ####getting collaborated events###if dont want collaborated event remove bottom section
                    collaborations = InterBranchCollaborations.objects.filter(collaboration_with = society).values_list('event_id')
                    #joining both the events list of collbarated and their own organised events
                    events = events.union(Events.objects.filter(pk__in=collaborations,publish_in_main_web= True)).order_by('-start_date','-event_date') 
                    ####################################################################################################################
            else:
                if primary == 1:
                    #when false getting latest five events
                    events = Events.objects.filter(publish_in_main_web= True).order_by('-start_date','-event_date')[:5]
                else:
                    #when False getting events 5 events which are upcoming, is published and is of particular society
                    events = Events.objects.filter(publish_in_main_web= True,event_organiser = society).order_by('-start_date','event_date')#[:5]
                    ####getting collaborated events###if dont want collaborated event remove bottom section and uncommment the list here -----------------------here
                    collaborations = InterBranchCollaborations.objects.filter(collaboration_with = society).values_list('event_id')
                    #joining both the events list of collbarated and their own organised events
                    events = events.union(Events.objects.filter(pk__in=collaborations,publish_in_main_web= True)).order_by('-start_date','-event_date')[:5]
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

        '''This function loads 6 events where first 2 are flasghsip and rest featured. If not available then 
            they would be latest event'''
        
        #getting all the flagship, featured and latest events
        flagship_events = Events.objects.filter(event_organiser=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),flagship_event =True , publish_in_main_web = True).order_by('-start_date','-event_date')
        featured_events=Events.objects.filter(event_organiser=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),is_featured=True,publish_in_main_web = True).order_by('-start_date','-event_date')
        latest_events = Events.objects.filter(event_organiser=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),publish_in_main_web = True).order_by('-start_date','-event_date')
        # Initialize lists and set to store the final events and unique event IDs
        final_events = []
        unique_event_ids = set()

        # Add flagship events to the final list up to 2 events
        for event in flagship_events:
            if event.id not in unique_event_ids:
                final_events.append(event)
                unique_event_ids.add(event.id)
            if len(final_events) == 2:
                break

        # Add featured events to the final list up to 4 events
        for event in featured_events:
            if event.id not in unique_event_ids:
                final_events.append(event)
                unique_event_ids.add(event.id)
            if len(final_events) == 6:
                break

        # If there are not enough featured events, replace missing ones with the latest normal events
        if len(final_events) < 6:
            for event in latest_events:
                if event.id not in unique_event_ids:
                    final_events.append(event)
                    unique_event_ids.add(event.id)
                if len(final_events) == 6:
                    break
        new_list=[]

        # create dictionary of featured events and then keep it on the list
        for i in final_events:
            featured_event_dict={}
            # store event obj in 'featured_event' key
            featured_event_dict['featured_event']=i
            # get banner image of every event and put it into the 'banner_image" key
            featured_event_dict['banner_image']=HomepageItems.load_event_banner_image(event_id=i.pk)
            # store the dict in the list
            new_list.append(featured_event_dict)
        
        return new_list
        
        
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

    def getAchievementCount():
        ''''Gets all the achievement count'''
        return Achievements.objects.all().count()
    
    def get_event_for_calender(request,primary):

        '''This function returns the events to show them on calender'''
        
        try:
            #getting all events according to the socities and affinity group primary value
            if primary == 1:
                all_events = Events.objects.filter(publish_in_main_web= True).order_by('-start_date','-event_date')
            else:
                society = SC_AG_Info.get_sc_ag_details(request,primary)
                #getting collaborated events
                collaborations = InterBranchCollaborations.objects.filter(collaboration_with = society).values_list('event_id')
                events = Events.objects.filter(publish_in_main_web= True,event_organiser = society).order_by('-start_date','-event_date')
                #joining both the events list of collbarated and their own organised events
                all_events = events.union(Events.objects.filter(pk__in=collaborations,publish_in_main_web= True))   
            #decalring empty dictionary for getting the event date and event
            #key is the date and event object is the value
            date_and_events = {}
            #iterating over each event
            for event in all_events:
                try:
                    #if date exists then formatting it
                    if event.event_date != None and event.start_date == None:
                        date = event.event_date.strftime("%Y-%m-%d")
                    else:
                        date = event.start_date.strftime("%Y-%m-%d")
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
                upcoming_event = Events.objects.filter(publish_in_main_web = True,start_date__gt=current_datetime).order_by('start_date')[:1]
            else:
                #getting the latest upcoming event for affinity groups and societies
                upcoming_event = Events.objects.filter(publish_in_main_web = True,start_date__gt=current_datetime,event_organiser = Chapters_Society_and_Affinity_Groups.objects.get(primary = primary)).order_by('start_date')#[:1]
                #getting collaborated upcoming event#if dont want this then remove bottom section and uncomment the list value to one, in the top line --------------------------------------------------------------------------here
                collaborations = InterBranchCollaborations.objects.filter(collaboration_with = society).values_list('event_id')
                #joining both the events list of collbarated and their own organised events
                upcoming_event = upcoming_event.union(Events.objects.filter(pk__in=collaborations,publish_in_main_web= True,start_date__gt=current_datetime)).order_by('start_date')[:1] 
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
            events = Events.objects.filter(event_organiser = Chapters_Society_and_Affinity_Groups.objects.get(primary = primary),is_featured = True,publish_in_main_web= True).order_by('-start_date','-event_date')[:4]
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
                roles = Roles_and_Position.objects.filter(is_sc_ag_eb_member = True,role_of = society,is_faculty=False).order_by('rank','role','role_of')
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

    def get_all_mega_events(primary):

        '''This function returns all mega_events of particular society that are published'''

        try:
            if primary == 1:
                return SuperEvents.objects.filter(publish_mega_event = True).order_by('-start_date')
            else:
                society = Chapters_Society_and_Affinity_Groups.objects.get(primary = primary)
                mega_events= SuperEvents.objects.filter(publish_mega_event = True,mega_event_of = society).order_by('-start_date')
                if(mega_events.exists()):
                    return mega_events
                else:
                    return False
        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
        
    def get_mega_event(mega_event_id):

        '''this function returns the mega event of specific id'''
        try:
            return SuperEvents.objects.get(id = mega_event_id)
        except SuperEvents.DoesNotExist:
            return False
        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False 
        
    def get_other_mega_event(mega_event_id):

        '''This function return other mega even apart from this one'''

        try:
            return SuperEvents.objects.filter(publish_mega_event=True).exclude(id=mega_event_id).order_by('-start_date')[:6]
        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    def all_events_of_mega_event(mega_event):

        '''This function returns all events of mega event'''
        try:

            events = Events.objects.filter(super_event_id = SuperEvents.objects.get(id = mega_event.id),publish_in_main_web=True).order_by('-start_date','-event_date')
          
            dic = {}
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
        
    def diving_gallery_images(all_images):

        '''This function returns all images in 4 different lists'''
        try:
            # initializing four empty list for storing all images in 4 different lists
            first_column = []
            second_column = []
            third_column = []
            fourth_column = []
            # four different starting indexes
            i = 0
            j = 1
            k = 2
            l = 3
            # two dimentional array of images of size(n X 4) where each column of image is getting stored in each list
            while i < len(all_images):
                first_column.append(all_images[i])
                i += 4
            while j < len(all_images):
                second_column.append(all_images[j])
                j += 4
            while k < len(all_images):
                third_column.append(all_images[k])
                k += 4
            while l < len(all_images):
                fourth_column.append(all_images[l])
                l += 4
            
            # returning the four lists as a tuple
            return first_column, second_column, third_column, fourth_column
            
        except Exception as e:
            HomepageItems.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False

    def get_top_5_performers():

        '''This function will return top 5 performers of all time'''

        performers = Members.objects.all().order_by('-completed_task_points')[:5]
        print(performers)
        return performers

    def get_top_5_teams():

        '''This function will return the top 3 teams'''
        
        teams = Teams.objects.all().order_by('-completed_task_points')[:5]
        return teams
                