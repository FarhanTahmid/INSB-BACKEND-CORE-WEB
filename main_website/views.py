from django.shortcuts import render,redirect
from django.http import HttpResponse
from central_events.models import Events,Event_Category
from central_branch.renderData import Branch
from chapters_and_affinity_group.models import SC_AG_Members
from main_website.models import Research_Papers,Blog,Achievements,News
from membership_development_team.renderData import MDT_DATA
from port.renderData import PortData,HandleVolunteerAwards
from port.models import Teams,Panels,Chapters_Society_and_Affinity_Groups,VolunteerAwards
from .renderData import HomepageItems
from django.conf import settings
from users.models import Panel_Members, User_IP_Address,Members
from users.models import User_IP_Address
import logging
from datetime import datetime
from django.http import JsonResponse
from system_administration.system_error_handling import ErrorHandling
import traceback
from .renderData import HomepageItems
from users.renderData import PanelMembersData
from users import renderData as userData
import json,requests
from insb_port import settings
from .models import *
from django.contrib import messages
from central_branch.renderData import Branch
from central_branch import views as cv
from central_events.models import InterBranchCollaborations,IntraBranchCollaborations
from django.views import View
from pytz import timezone as tz
from system_administration.models import system


logger=logging.getLogger(__name__)

# Create your views here.
def homepage(request):
    try:
        bannerItems=HomepageItems.getHomepageBannerItems()
        bannerWithStat=HomepageItems.getBannerPictureWithStat()
        HomepageItems.get_ip_address(request)
        #getting all the thoughts
        all_thoughts = Branch.get_all_homepage_thoughts()

        # get recent 6 news
        get_recent_news=News.objects.filter().order_by('-news_date')[:6]
        # get recent 6 Blogs
        get_recent_blogs=Blog.objects.filter(publish_blog=True).order_by('-date')[:6]
        # get featured events of branch
        get_featured_events=HomepageItems.load_featured_events(sc_ag_primary=1)
        # get volunteer of the months
        # get_volunteers_of_the_month=VolunteerOfTheMonth.objects.all().order_by('-pk')

        # get current panel of Branch
        current_panel_pk=PortData.get_current_panel()
        # get awards for the current panel
        awards_of_current_panel=HandleVolunteerAwards.load_awards_for_panels(request=request,panel_pk=current_panel_pk)

        #only for countdown
        countdown = system.objects.first()
        if countdown.count_down is not None:
            local_timezone = tz('Asia/Dhaka')
            start_time = countdown.count_down.astimezone(local_timezone)
            start_time = start_time.replace(tzinfo=None)
        else:
            start_time = None

        button_enabled = False
        if request.user.is_superuser or request.user.is_staff:
            button_enabled = True

    
        context={
            'banner_item':bannerItems,
            'banner_pic_with_stat':bannerWithStat,
            'featured_events':get_featured_events,
            'media_url':settings.MEDIA_URL,
            'all_member_count':HomepageItems.getAllIEEEMemberCount(),
            'event_count':HomepageItems.getEventCount(),
            'achievement_count':HomepageItems.getAchievementCount(),
            'recent_news':get_recent_news,
            'recent_blogs':get_recent_blogs,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            'all_thoughts':all_thoughts,
            # 'all_vom':get_volunteers_of_the_month,
            'awards':awards_of_current_panel,
            'start_time':start_time,#only for countdown
            'button_enabled':button_enabled,
        }
        return render(request,"LandingPage/homepage.html",context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

class LoadAwards(View):
    def get(self,request):
        award_pk = request.GET.get('award_pk')
        
        if(award_pk=="0"):
            # get current panel of branch
            current_panel_pk=PortData.get_current_panel()
            # get the highest ranked award
            highest_ranked_award_in_the_panel=VolunteerAwards.objects.filter(panel=Panels.objects.get(pk=current_panel_pk)).first()
            if(highest_ranked_award_in_the_panel is None):
                
                return JsonResponse(
                    {
                    'message':message,
                    }
                    ,status=200,safe=False
                )
            else:
                award_winners=HandleVolunteerAwards.load_award_winners(award_pk=highest_ranked_award_in_the_panel.pk,request=request)
                if(award_winners==False):
                    message="No Member was found to be a winner in this Award"
                    return JsonResponse({
                        'message':message,
                    },status=200,safe=False)
                else:
                    data=[]
                    for i in award_winners:
                        data.append({
                            "picture":str(i.award_reciever.user_profile_picture),
                            "name":i.award_reciever.name,
                            "team":str(i.award_reciever.team),
                            "position":str(i.award_reciever.position),
                            "contributions":i.contributions
                        })
                    json_data={
                        'award_name':highest_ranked_award_in_the_panel.volunteer_award_name,
                        'winners':data
                    }
                    return JsonResponse(
                        data=json_data,
                        status=200,
                        safe=False
                    )
            
        else:
            # get award details
            get_award=HandleVolunteerAwards.load_award_details(request=request,award_pk=award_pk)
            # get award winners by award_pk
            award_winners=HandleVolunteerAwards.load_award_winners(request=request,award_pk=award_pk)
            if(len(award_winners) == 0):
                message="No Member was found to be a winner in this Award"
                return JsonResponse({
                    'message':message,
                },status=400,safe=False)
            else:
                data=[]
                for i in award_winners:
                    data.append({
                        "picture":str(i.award_reciever.user_profile_picture),
                        "name":i.award_reciever.name,
                        "team":str(i.award_reciever.team),
                        "position":str(i.award_reciever.position),
                        "contributions":i.contributions
                    })
                json_data={
                    'award_name':get_award.volunteer_award_name,
                    'winners':data
                }
                return JsonResponse(
                    data=json_data,
                    status=200,
                    safe=False
                )
            

##################### EVENT WORKS ####################

def event_homepage(request):

    '''This view function loads all the events for the events homepage'''
    
    try:
        all_events = HomepageItems.load_all_events(request,True,1)
        latest_five_events = HomepageItems.load_all_events(request,False,1)
        date_and_event = HomepageItems.get_event_for_calender(request,1)
        upcoming_event = HomepageItems.get_upcoming_event(request,1)
        upcoming_event_banner_picture = HomepageItems.load_event_banner_image(upcoming_event)
        all_mega_events = HomepageItems.get_all_mega_events(1)
        all_categories = Event_Category.objects.filter(event_category_for= Chapters_Society_and_Affinity_Groups.objects.get(primary = 1))
        print(all_categories)
        has_mega_events=True
        if(all_mega_events==False):
            has_mega_events=False
        
        # prepare event stat list for event category with numbers
        get_event_stat=userData.getTypeOfEventStats(request,1)
        event_stat=[]
        # prepare data from the tuple
        categories, count, percentage_mapping = get_event_stat
        for category, count in zip(categories, count):
            event_stat_dict={}
            # get event name
            event_stat_dict['name']=category
            # get event count according to category
            event_stat_dict['value']=count
            # append the dict to list
            event_stat.append(event_stat_dict)
        
        # prepare yearly event stat list for Branch
        get_yearly_events=userData.getEventNumberStat(request,1)
        # prepare years
        get_years=get_yearly_events[0]
        # prepare event counts according to years
        get_yearly_event_count=get_yearly_events[1]

        if upcoming_event:
            local_timezone = tz('Asia/Dhaka')
            modified_start_time = upcoming_event.start_date.astimezone(local_timezone)
            modified_start_time = modified_start_time.replace(tzinfo=None)
        else:
            modified_start_time = None

        context = {
            'page_title':"Events",
            'page_subtitle':"IEEE NSU Student Branch",
            'all_events':all_events,
            'media_url':settings.MEDIA_URL,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            'latest_five_event':latest_five_events,
            'date_and_event':date_and_event,
            'upcoming_event':upcoming_event,
            'upcoming_event_banner_picture':upcoming_event_banner_picture,
            'data':event_stat,
            'years':get_years,
            'yearly_event_count':get_yearly_event_count,
            'all_mega_events':all_mega_events,
            'has_mega_events':has_mega_events,
            'all_categories':all_categories,
            'modified_start_time':modified_start_time,
        }

        return render(request,'Events/events_homepage.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    
    
def event_details(request,event_id):
 
    '''Loads details for the corresponding event page on site'''
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            satisfaction = request.POST.get('satisfaction')
            comment = request.POST.get('comment')

            if(Branch.add_feedback(event_id=event_id, name=name,email=email,satisfaction=satisfaction,comment=comment)):
                messages.success(request,'We have received it. Thank you for your feedback!')
            else:
                messages.warning(request,'Sorry you couldn\'t read us at the moment. Please try again later.')

            return redirect('main_website:event_details', event_id)
        try:
            get_event = Events.objects.get(id = event_id)
            
            get_inter_branch_collab=InterBranchCollaborations.objects.filter(event_id=get_event.pk)
            get_intra_branch_collab=IntraBranchCollaborations.objects.filter(event_id=get_event.pk).first()
            
            has_interbranch_collab=False
            has_intrabranch_collab=False
            
            if(len(get_inter_branch_collab) > 0):
                has_interbranch_collab=True
            if(get_intra_branch_collab is not None):
                has_intrabranch_collab=True
                        
            # get host
            if(get_event.publish_in_main_web):
                event_banner_image = HomepageItems.load_event_banner_image(event_id=event_id)
                event_gallery_images = HomepageItems.load_event_gallery_images(event_id=event_id)

                context = {
                    'is_live':True, #This enables the header and footer along with the wavy
                    'page_title':get_event.event_name,
                    'page_subtitle':get_event.event_organiser,
                    "event":get_event,
                    'media_url':settings.MEDIA_URL,
                    'event_banner_image' : event_banner_image,
                    'event_gallery_images' : event_gallery_images,
                    'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
                    'has_interbranch_collab':has_interbranch_collab,
                    'has_intrabranch_collab':has_intrabranch_collab,
                    'inter_collaborations':get_inter_branch_collab,
                    'intra_collab':get_intra_branch_collab,
                }
                return render(request,"Events/event_description_main.html", context)
        except Events.DoesNotExist:
            return cv.custom_404
        else:
            return redirect('main_website:event_homepage')
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)


# ###################### ACHIEVEMENTS ##############################

def achievements(request):
    
    '''This view function loads all achievements'''

    try:
        load_all_achievements=Achievements.objects.all().order_by('-award_winning_datefield__year','-award_winning_datefield__month')
        context={
            'page_title':"Achievements",
            'achievements':load_all_achievements,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch

        }
        
        return render(request,"Activities/achievements.html",context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def news(request):
    
    try:
        # load news of insb
        load_all_news=News.objects.all().order_by('-news_date')
        
        # apis to get online news
        url_robotics=f'https://newsdata.io/api/1/news?apikey={settings.NEWS_API_KEY}&q=robotics&language=en&category=education,science,technology'
        url_wie_news=f'https://newsdata.io/api/1/news?apikey={settings.NEWS_API_KEY}&q="women%20in%20STEM"&category=technology'
        url_ai_machine_learning=f'https://newsdata.io/api/1/news?apikey={settings.NEWS_API_KEY}&q="artificial%20neural%20network"%20OR%20"deep%20learning"&language=en&category=technology,top '

        # keeping urls as list
        url_list=[url_robotics,url_ai_machine_learning,url_wie_news]
        
        json_datas=[]
        # extracting response from the apis and keeping all the three datas of the api in a list
        for url in url_list:
            response=requests.get(url)
            if(response.status_code==200):
                # if response is okay then load data
                json_datas.append(json.loads(response.text))
        
        all_online_news=[]
        # extracting article results
        for i in json_datas:
            articles=i.get('results',[])        
            for article in articles:
                # extracting article values
                title=article.get('title',[])
                article_link=article.get('link',[])
                article_description=article.get('description',[])
                article_picture=article.get('image_url',[])
                article_creator=article.get('creator',[])
                article_id=article.get('article_id',[])
                article_publish_date=article.get('pubDate',[])
                # storing all articles as dictionary key value items
                news_item={
                    'article_id':article_id,
                    'pubDate':article_publish_date,
                    'title':title,
                    'article_link':article_link,
                    'article_description':article_description,
                    'article_picture':article_picture,
                    'article_creator':article_creator
                }
                # storing all articles in a list
                all_online_news.append(news_item)
        has_online_news=False
        if(len(all_online_news)>0):
            has_online_news=True
        context={
            'page_title':"News",
            'all_news':load_all_news,
            'all_online_news':all_online_news,
            'has_online_news':has_online_news,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch

            
        }
        return render(request,'Activities/news.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
def news_description(request,pk):
    
    try:
        # get news
        news=News.objects.get(pk=pk)
        
        # get recent 3 news
        recent_news=News.objects.all().order_by('-news_date').exclude(pk=pk)[:3]
        
        # get recent 5 blogs
        recent_blogs=Blog.objects.filter(publish_blog=True).order_by('-date')[:5]
        
        context={
            'page_title':news.news_title,
            'page_subtitle':"IEEE NSU Student Branch",
            'news':news,
            'recent_news':recent_news,
            'recent_blogs':recent_blogs,
            
        }
        return render(request,"Activities/news_description.html",context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)


############################## SC_AG ############################################
def rasPage(request):

    '''This view function loads the ras main web page'''
    
    try:
        #getting RAS object
        society = Chapters_Society_and_Affinity_Groups.objects.get(primary = 3)
        # get mega events
        all_mega_events=HomepageItems.get_all_mega_events(primary=3)
        organised_events = Events.objects.filter(event_organiser = society,publish_in_main_web = True).order_by('-event_date')
        has_mega_events=True
        if(all_mega_events==False):
            has_mega_events=False
        #getting featured events of RAS   
        featured_events = HomepageItems.get_featured_events_for_societies(3)
        
        #getting faculty member
        faculty_advisor = HomepageItems.get_faculty_advisor_for_society(request,3)
        #getting eb members for the particular society
        eb_members = HomepageItems.get_eb_members_for_society(request,3)
        
        # getRasAbout=society_ag.Ras.get_ras_about()
            
        # if getRasAbout is False:
        #     return HttpResponse("GG")

        if request.method == "POST":
            #when user hits submit button on main page
            if request.POST.get('submit'):
                #getting the user's details
                name = request.POST.get('user_name')
                email = request.POST.get('user_email')
                message = request.POST.get('user_message')
                #passing them as arguments to the function to save the data
                if HomepageItems.save_feedback_information(request,3,name,email,message):
                    messages.success(request,"You have reached us! Thanks for your feedback")  
                else:
                    messages.error(request,"Sorry! Try to contact us later") 
                return redirect("main_website:ras_home")
                
            
        context={
            'is_live':True, #This enables the header and footer of the page along with wavy   
            'society':society,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            'media_url':settings.MEDIA_URL,
            'featured_events':featured_events,
            'faculty_advisor':faculty_advisor,
            'eb_members':eb_members,
            'page_title':society.page_title,
            'page_subtitle':society.secondary_paragraph,
            'all_mega_events':all_mega_events,
            'has_mega_events':has_mega_events,
            'organised_events':organised_events,
        }
        return render(request,'Society_AG/sc_ag.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
def pesPage(request):

    '''This view function loads the pes main web page'''
    
    try:
        #getting object of PES
        society = Chapters_Society_and_Affinity_Groups.objects.get(primary = 2)
        all_mega_events=HomepageItems.get_all_mega_events(primary=2)
        organised_events = Events.objects.filter(event_organiser = society,publish_in_main_web = True).order_by('-event_date')
        has_mega_events=True
        if(all_mega_events==False):
            has_mega_events=False
            
        #getting featured events of PES   
        featured_events = HomepageItems.get_featured_events_for_societies(2)

        #getting faculty member
        faculty_advisor = HomepageItems.get_faculty_advisor_for_society(request,2)
        #getting eb members for the particular society
        eb_members = HomepageItems.get_eb_members_for_society(request,2)


        if request.method == "POST":
            #when user hits submit button on main page
            if request.POST.get('submit'):
                #getting the user's details
                name = request.POST.get('user_name')
                email = request.POST.get('user_email')
                message = request.POST.get('user_message')
                #passing them as arguments to the function to save the data
                if HomepageItems.save_feedback_information(request,2,name,email,message):
                    messages.success(request,"You have reached us! Thanks for your feedback")  
                else:
                    messages.error(request,"Sorry! Try to contact us later") 
                return redirect("main_website:pes_home")
                
        context={
            'is_live':True, #This enables the header and footer of the page along with wavy    
            'society':society,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            'media_url':settings.MEDIA_URL,
            'featured_events':featured_events,
            'faculty_advisor':faculty_advisor,
            'eb_members':eb_members,
            'page_title':society.page_title,
            'page_subtitle':society.secondary_paragraph,
            'all_mega_events':all_mega_events,
            'has_mega_events':has_mega_events,
            'organised_events':organised_events,
        }
        return render(request,'Society_AG/sc_ag.html',context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
def iasPage(request):

    '''This view function loads the ias main web page'''

    try:
        #getting object of IAS
        society = Chapters_Society_and_Affinity_Groups.objects.get(primary = 4)
        all_mega_events=HomepageItems.get_all_mega_events(primary=4)
        organised_events = Events.objects.filter(event_organiser = society,publish_in_main_web = True).order_by('-event_date')
        has_mega_events=True
        if(all_mega_events==False):
            has_mega_events=False
        #getting featured events of IAS   
        featured_events = HomepageItems.get_featured_events_for_societies(4)

        #getting faculty member
        faculty_advisor = HomepageItems.get_faculty_advisor_for_society(request,4)
        #getting eb members for the particular society
        eb_members = HomepageItems.get_eb_members_for_society(request,4)

        if request.method == "POST":
            #when user hits submit button on main page
            if request.POST.get('submit'):  
                #getting the user's details
                name = request.POST.get('user_name')
                email = request.POST.get('user_email')
                message = request.POST.get('user_message')
                #passing them as arguments to the function to save the data
                if HomepageItems.save_feedback_information(request,4,name,email,message):
                    messages.success(request,"You have reached us! Thanks for your feedback")  
                else:
                    messages.error(request,"Sorry! Try to contact us later") 
                return redirect("main_website:ias_home")
                  
        context={
            'is_live':True, #This enables the header and footer of the page along with wavy    
            'society':society,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            'media_url':settings.MEDIA_URL,
            'featured_events':featured_events,
            'faculty_advisor':faculty_advisor,
            'eb_members':eb_members,
            'page_title':society.page_title,
            'page_subtitle':society.secondary_paragraph,
            'all_mega_events':all_mega_events,
            'has_mega_events':has_mega_events,
            'organised_events':organised_events,

        }
        return render(request,'Society_AG/sc_ag.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
def wiePage(request):

    '''This view function loads the wie main web page'''
    
    try:
        #getting object of WIE
        society = Chapters_Society_and_Affinity_Groups.objects.get(primary = 5)
        all_mega_events=HomepageItems.get_all_mega_events(primary=5)
        organised_events = Events.objects.filter(event_organiser = society,publish_in_main_web = True).order_by('-event_date')
        has_mega_events=True
        if(all_mega_events==False):
            has_mega_events=False
        #getting featured events of WIE    
        featured_events = HomepageItems.get_featured_events_for_societies(5)

        #getting faculty member
        faculty_advisor = HomepageItems.get_faculty_advisor_for_society(request,5)
        #getting eb members for the particular society
        eb_members = HomepageItems.get_eb_members_for_society(request,5)

        if request.method == "POST":
            #when user hits submit button on main page
            if request.POST.get('submit'):
                #getting the user's details
                name = request.POST.get('user_name')
                email = request.POST.get('user_email')
                message = request.POST.get('user_message')
                #passing them as arguments to the function to save the data
                if HomepageItems.save_feedback_information(request,5,name,email,message):
                    messages.success(request,"You have reached us! Thanks for your feedback")  
                else:
                    messages.error(request,"Sorry! Try to contact us later") 
                return redirect("main_website:wie_home")
                
            
        context={
            'is_live':True, #This enables the header and footer of the page along with wavy    
            'society':society,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            'media_url':settings.MEDIA_URL,
            'featured_events':featured_events,
            'faculty_advisor':faculty_advisor,
            'eb_members':eb_members,
            'page_title':society.page_title,
            'page_subtitle':society.secondary_paragraph,
            'all_mega_events':all_mega_events,
            'has_mega_events':has_mega_events,
            'organised_events':organised_events,

        }
        return render(request,'Society_AG/sc_ag.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def events_for_sc_ag(request,primary):

    ''' This view function loads the events for the society affinity group event homepage'''
    try:

        society = Chapters_Society_and_Affinity_Groups.objects.get(primary = primary)
        all_events = HomepageItems.load_all_events(request,True,primary)
        all_mega_events=HomepageItems.get_all_mega_events(primary=primary)
        organised_events = Events.objects.filter(event_organiser = society,publish_in_main_web = True).order_by('-event_date')
        latest_five_events = HomepageItems.load_all_events(request,False,primary)
        date_and_event = HomepageItems.get_event_for_calender(request,primary)
        upcoming_event = HomepageItems.get_upcoming_event(request,primary)
        upcoming_event_banner_picture = HomepageItems.load_event_banner_image(upcoming_event)
        all_categories = Event_Category.objects.filter(event_category_for= Chapters_Society_and_Affinity_Groups.objects.get(primary = primary))

        has_mega_events=True
        if(all_mega_events==False):
            has_mega_events=False

        # prepare event stat list for event category with numbers
        get_event_stat=userData.getTypeOfEventStats(request,primary)
        event_stat=[]
        # prepare data from the tuple
        categories, count, percentage_mapping = get_event_stat
        for category, count in zip(categories, count):
            event_stat_dict={}
            # get event name
            event_stat_dict['name']=category
            # get event count according to category
            event_stat_dict['value']=count
            # append the dict to list
            event_stat.append(event_stat_dict)
        
        # prepare yearly event stat list for Branch
        get_yearly_events=userData.getEventNumberStat(request,primary)
        # prepare years
        get_years=get_yearly_events[0]
        # prepare event counts according to years
        get_yearly_event_count=get_yearly_events[1]

        if upcoming_event:
            local_timezone = tz('Asia/Dhaka')
            modified_start_time = upcoming_event.start_date.astimezone(local_timezone)
            modified_start_time = modified_start_time.replace(tzinfo=None)
        else:
            modified_start_time = None

        context = {
            'is_sc_ag':True,
            'society':society,
            'page_title': 'Events',
            'page_subtitle':society.short_form,
            'all_events':all_events,
            'all_mega_events':all_mega_events,
            'media_url':settings.MEDIA_URL,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            'latest_five_event':latest_five_events,
            'date_and_event':date_and_event,
            'upcoming_event':upcoming_event,
            'upcoming_event_banner_picture':upcoming_event_banner_picture,
            'data':event_stat,
            'years':get_years,
            'yearly_event_count':get_yearly_event_count,
            'has_mega_events':has_mega_events,
            'organised_events':organised_events,
            'all_categories':all_categories,
            'modified_start_time':modified_start_time,
        }



        return render(request,'Events/events_homepage.html',context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)



######################## BLOG WORKS ################################


def blogs(request):

    '''Loads the blog page where all blog is shown'''

    try:
        get_all_blog= Blog.objects.filter(publish_blog=True).order_by('-date')
        get_all_categories = Blog_Category.objects.all()
        context={
            'page_title':"Blogs",
            'blogs':get_all_blog,
            'categories':get_all_categories,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
        }
        return render(request,"Publications/Blog/blog.html",context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)


def write_blogs(request):
    '''Creates a form and allows user to give a request to publish their blogs in the site'''

    try:
        # load all sc ag and Branch
        load_all_sc_ag=Chapters_Society_and_Affinity_Groups.objects.all().order_by('primary')
        # load all blog categories
        load_all_blog_category=Blog_Category.objects.all()
        
        if(request.method=="POST"):
            if(request.POST.get('submit_blog')):
                writer_ieee_id=request.POST['writer_ieee_id']
                writer_name=request.POST['writer_name']
                group=request.POST.get('group')
                blog_title=request.POST['blog_title']
                blog_category=request.POST.get('blog_category')
                blog_short_description=request.POST['blog_short_description']
                blog_description=request.POST['blog_description']
                blog_banner=request.FILES['blog_banner_picture']
                try:
                    if(group=="" and blog_category==""):
                            new_requested_blog=Blog.objects.create(
                            ieee_id=writer_ieee_id,writer_name=writer_name,title=blog_title,
                            date=datetime.today(),
                            short_description=blog_short_description,blog_banner_picture=blog_banner,
                            description=blog_description,
                            is_requested=True
                            )
                            new_requested_blog.save()

                    elif(group != "" and blog_category==""):
                            new_requested_blog=Blog.objects.create(
                            ieee_id=writer_ieee_id,writer_name=writer_name,title=blog_title,
                            date=datetime.today(),
                            short_description=blog_short_description,blog_banner_picture=blog_banner,
                            description=blog_description,branch_or_society=Chapters_Society_and_Affinity_Groups.objects.get(primary=group),
                            is_requested=True
                            )
                            new_requested_blog.save()

                    elif(group=="" and blog_category != ""):
                            new_requested_blog=Blog.objects.create(
                            ieee_id=writer_ieee_id,writer_name=writer_name,title=blog_title,
                            category=Blog_Category.objects.get(pk=blog_category),date=datetime.today(),
                            short_description=blog_short_description,blog_banner_picture=blog_banner,
                            description=blog_description,
                            is_requested=True
                            )
                            new_requested_blog.save()

                    else:
                            new_requested_blog=Blog.objects.create(
                                ieee_id=writer_ieee_id,writer_name=writer_name,title=blog_title,
                                category=Blog_Category.objects.get(pk=blog_category),date=datetime.today(),
                                short_description=blog_short_description,blog_banner_picture=blog_banner,
                                description=blog_description,branch_or_society=Chapters_Society_and_Affinity_Groups.objects.get(primary=group),
                                is_requested=True
                            )
                            new_requested_blog.save()
                    messages.success(request,"We have received your blog publishing request. We will publish it soon. Thank you!")
                    return redirect('main_website:write_blogs')
                except Exception as e:
                    messages.warning(request,"Something went wrong! Please try again!")
                    logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
                    ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
                    return redirect('main_website:write_blogs')
                
        context={
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            'all_sc_ag':load_all_sc_ag,
            'blog_categories':load_all_blog_category,
            'page_title':"Write a Blog",
            'page_subtitle':"""Unleash your intellect on the realms of science and technology, guiding us towards a sustainable future with your insights on power and energy.""",
            
        }
        return render(request,"Get Involved/Write Blog/write_blog.html",context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def blog_description(request,pk):

    try:
        # get the blog
        get_blog=Blog.objects.get(pk=pk)
        # this shows IEEE NSU Student branch as default if there is no group selected in Blog
        if(get_blog.branch_or_society is None):
            society_name="IEEE NSU Student Branch"
        else:
            society_name=get_blog.branch_or_society.group_name
        
        # get recent blogs
        get_recent_blogs=Blog.objects.filter(publish_blog=True).order_by('-date').exclude(pk=pk)[:3]
        # get recent news
        get_recent_news=News.objects.all().order_by('-news_date')[:5]
            
        context={
            'page_title':get_blog.title,
            'page_subtitle':society_name,
            'blog':get_blog,
            'recent_blogs':get_recent_blogs,
            'recent_news':get_recent_news,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch

        }
        return render(request, 'Publications/Blog/blog_description_main.html',context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)


######################### RESEARCH PAPER WORKS ###########################

def research_Paper(request):

    '''Loads all research papers for the corresponding page'''

    try:
        get_all_research_papers = Research_Papers.objects.filter(publish_research=True).order_by('-publish_date')
        
        context={
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            'page_title':"Research Papers",
            'page_subtitle':"IEEE NSU Student Branch",
            "all_research_papers":get_all_research_papers
        } 
        return render(request,"Publications/Research Paper/research_paper.html",context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def add_research_form(request):

    '''Handles form responses for add research paper form'''

    try:
        # get research categories
        research_categories=ResearchCategory.objects.all()
        # load all sc ag and Branch
        load_all_sc_ag=Chapters_Society_and_Affinity_Groups.objects.all().order_by('primary')

        if(request.method=="POST"):
            if(request.POST.get('submit_paper')):
                author_names=request.POST['author_names']
                group=request.POST.get('group')
                paper_title=request.POST['paper_title']
                research_category=request.POST.get('research_category')
                abstract_description=request.POST['abstract_description']
                paper_link=request.POST['paper_link']
                research_banner_picture=request.FILES['research_banner_picture']
                
                if(research_category == ""):
                    new_research_request=Research_Papers.objects.create(
                        title=paper_title,
                        group=Chapters_Society_and_Affinity_Groups.objects.get(primary=group),
                        research_banner_picture=research_banner_picture,
                        author_names=author_names,short_description=abstract_description,
                        publish_date=datetime.today(),publication_link=paper_link,
                        is_requested=True
                    )
                    new_research_request.save()
                    messages.success(request,"Your request has been submitted! Thank you.")
                    return redirect('main_website:add_research')
                else:
                    new_research_request=Research_Papers.objects.create(
                        title=paper_title,category=ResearchCategory.objects.get(pk=research_category),
                        group=Chapters_Society_and_Affinity_Groups.objects.get(primary=group),
                        research_banner_picture=research_banner_picture,
                        author_names=author_names,short_description=abstract_description,
                        publish_date=datetime.today(),publication_link=paper_link,
                        is_requested=True
                    )
                    new_research_request.save()
                    messages.success(request,"Your request has been submitted! Thank you.")
                    return redirect('main_website:add_research')                   
        context={
            'page_title':"Add Research Papers",
            'page_subtitle':"""Participate in the IEEE NSU Student Branch's academic community, share your research papers, and collaborate for impactful innovation.""",
            'research_categories':research_categories,
            'all_sc_ag':load_all_sc_ag,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch

        }
        
        return render(request,"Get Involved/Add Research/research_paper_form.html",context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
######################### Magazine WORKS ###########################

def magazines(request):
    '''Loads all the magazines for the corresponding page'''

    try:

        get_all_magazines=Magazines.objects.all().order_by('-publish_date')
        context={
            'page_title':"Magazines",
            'all_magazines':get_all_magazines,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
        }
        return render(request,"Publications/Magazines/magazine.html",context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

######################### GALLERY WORKS ###########################
def gallery(request):

    try:

        # get all image and videos
        all_images=GalleryImages.objects.all().order_by('-pk')
        all_videos=GalleryVideos.objects.all().order_by('-pk')

        divided_image = HomepageItems.diving_gallery_images(all_images)

        context={
            'page_title':"Gallery",
            'all_images':all_images,
            'all_videos':all_videos,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            'first_column_images': divided_image[0],
            'second_column_images': divided_image[1],
            'third_column_images': divided_image[2],
            'fourth_column_images': divided_image[3],
        }
        return render(request, 'Publications/Gallery/gallery.html',context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)


# Memeber works

def current_panel_members(request):

    try:
        # load all panels at first
        get_all_panels=Branch.load_all_panels()
        get_current_panel=Branch.load_current_panel()
        has_current_panel=True
        if(get_current_panel is not None):
            # get the latest panel of branch and redirect to there
            has_current_panel=True
            
            get_current_panel_members=Branch.load_panel_members_by_panel_id(panel_id=get_current_panel.pk)
            
            # TODO:add algo to add SC AG Faculty and Branch Counselor

            branch_counselor=[]
            sc_ag_faculty_advisors=PortData.get_sc_ag_faculty_members(request=request)
            mentors=[]
            branch_chair=[]
            branch_eb=[]
            sc_ag_chair=PortData.get_branch_ex_com_from_sc_ag(request=request)
            for i in get_current_panel_members:
                if (i.position.role_of.primary==1):
                    if(i.position.is_faculty):
                        branch_counselor.append(i)
                    elif(i.position.is_eb_member):
                        if(i.position.role=='Chair'):
                            branch_chair.append(i)
                        elif(i.position.is_mentor):
                            mentors.append(i)
                        else:
                            branch_eb.append(i)
            # check of having different members
            has_branch_counselor=False
            has_sc_ag_faculty_advisor=False
            has_mentors=False
            has_branch_chair=False
            has_branch_eb=False
            has_sc_ag_chair=False
            if(len(branch_counselor)>0):
                has_branch_counselor=True
            if(len(sc_ag_faculty_advisors)>0):
                has_sc_ag_faculty_advisor=True
            if(len(mentors)>0):
                has_mentors=True
            if(len(branch_chair)>0):
                has_branch_chair=True
            if(len(branch_eb)>0):
                has_branch_eb=True
            if(len(sc_ag_chair)>0):
                has_sc_ag_chair=True
            
                
            context={
                'has_branch_counselor':has_branch_counselor,'has_sc_ag_faculty_advisor':has_sc_ag_faculty_advisor,'has_mentors':has_mentors,'has_branch_chair':has_branch_chair,'has_branch_eb':has_branch_eb,'has_sc_ag_chair':has_sc_ag_chair,
                'has_current_panel':has_current_panel,
                'panels':get_all_panels,
                'branch_counselor':branch_counselor,
                'sc_ag_faculty_advisors':sc_ag_faculty_advisors,
                'mentors':mentors,
                'chair':branch_chair,
                'eb':branch_eb,
                'sc_ag_chair':sc_ag_chair,
                'page_title':"Current Panel of IEEE NSU SB",
                'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            }
        else:
            has_current_panel=False
            get_the_latest_panel_of_branch=Panels.objects.filter(panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=1)).order_by('-year').first()

            return redirect('main_website:panel_members_previous',get_the_latest_panel_of_branch.year)
        
        return render(request,'Members/Panel/panel_members.html',context)

    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def panel_members_page(request,year):

    try:

        get_all_panels=Branch.load_all_panels()
        get_panel=Branch.get_panel_by_year(year)
        get_panel_members=Branch.load_panel_members_by_panel_id(panel_id=get_panel.pk)
        # TODO:add algo to add SC AG Faculty and EB
        branch_counselor=[]
        sc_ag_faculty_advisors=PortData.get_sc_ag_faculty_by_year(panel_year=get_panel.year,request=request)
        mentors=[]
        branch_chair=[]
        branch_eb=[]
        sc_ag_chair=PortData.get_branch_ex_com_from_sc_ag_by_year(panel_year=get_panel.year,request=request)
        # alumni_member=[]
        
        for i in get_panel_members:
            if (i.position.role_of.primary==1):
                if(i.position.is_faculty):
                    branch_counselor.append(i)
                elif(i.position.is_eb_member):
                    if(i.position.role=='Chair'):
                        branch_chair.append(i)
                    elif(i.position.is_mentor):
                        mentors.append(i)
                    else:
                        branch_eb.append(i)
        
        #TODO: fix the issue of branch chair showing twice in the algo
        
        
        # check of having different members
        has_branch_counselor=False
        has_sc_ag_faculty_advisor=False
        has_mentors=False
        has_branch_chair=False
        has_branch_eb=False
        has_sc_ag_chair=False
        
        if(len(branch_counselor)>0):
            has_branch_counselor=True
        if(len(sc_ag_faculty_advisors)>0):
            has_sc_ag_faculty_advisor=True
        if(len(mentors)>0):
            has_mentors=True
        if(len(branch_chair)>0):
            has_branch_chair=True
        if(len(branch_eb)>0):
            has_branch_eb=True
        if(len(sc_ag_chair)>0):
            has_sc_ag_chair=True
        
        context={
            'has_branch_counselor':has_branch_counselor,'has_sc_ag_faculty_advisor':has_sc_ag_faculty_advisor,'has_mentors':has_mentors,'has_branch_chair':has_branch_chair,'has_branch_eb':has_branch_eb,'has_sc_ag_chair':has_sc_ag_chair,
            'panels':get_all_panels,
            'branch_counselor':branch_counselor,
            'sc_ag_faculty_advisors':sc_ag_faculty_advisors,
            'mentors':mentors,
            'chair':branch_chair,
            'eb':branch_eb,
            'sc_ag_chair':sc_ag_chair,
            'has_current_panel':True,
            'page_title':f"Executive Panel - {year}",
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
        }
        return render(request,'Members/Panel/panel_members.html',context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc() + "<br>year = " + year)
        return cv.custom_500(request)

def officers_page(request):

    try:

        # get all teams of IEEE NSU Student Branch
        get_teams=PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
        # get all officers of branch. to get the current officers load the current panel of branch
        get_current_panel=Branch.load_current_panel()
        if(get_current_panel is None):
            # there is no current panel, so there will be no officer, so pass just the team contexts.
            context={
            'page_title':'Officers of IEEE NSU Student Branch',
            'teams':get_teams,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            }
        else:
            get_panel_officers=PanelMembersData.get_officer_members_from_branch_panel(request=request,panel=get_current_panel.pk)
            co_ordinators=[]
            incharges=[]
            for i in get_panel_officers:
                if(i.member.position.is_co_ordinator):
                    co_ordinators.append(i)
                else:
                    incharges.append(i)
            
            context={
                'page_title':'Officers of IEEE NSU Student Branch',
                'teams':get_teams,
                'co_ordinators':co_ordinators,
                'incharges':incharges,
                'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            }
        return render(request,'Members/Officers/officer_page.html',context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def team_based_officers_page(request,team_primary):

    try:
        # get the team
        try:
            team=Teams.objects.get(primary=team_primary)
            team_name=team.team_name
        except Teams.DoesNotExist:
            team_name=""
        
        # get all teams of IEEE NSU Student Branch
        get_teams=PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
        
        # get current panel of branch to load officers of the team from there
        get_current_panel=Branch.load_current_panel()
        if(get_current_panel is None):
            context={
                'page_title':f"Officers - {team_name}",
                'teams':get_teams,
                'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
                }
        else:
            # get team members
            team_members=PanelMembersData.get_members_of_teams_from_branch_panel(request=request,team_primary=team_primary,panel_id=get_current_panel.pk)
            co_ordinators=[]
            incharges=[]
            for member in team_members:
                if(member.position.is_officer):
                    if(member.position.is_co_ordinator):
                        co_ordinators.append(member)
                    else:
                        incharges.append(member)          
            
            context={
                'page_title':f"Officers - {team_name}",
                'teams':get_teams,
                'co_ordinators':co_ordinators,
                'incharges':incharges,
                'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            }
        return render(request,'Members/Officers/officer_page.html',context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def volunteers_page(request):

    try:

        # get all volunteers of branch. to get the current volunteers load the current panel of branch
        get_current_panel=Branch.load_current_panel()
        if(get_current_panel is None):
            # there is no current panel, so there will be no officer, so pass just the team contexts.
            context={
            'page_title':'Officers of IEEE NSU Student Branch',
            }
        else:
            get_panel_officers=PanelMembersData.get_volunteer_members_from_branch_panel(request=request,panel=get_current_panel.pk)
            core_volunteers=[]
            team_volunteers=[]
            for i in get_panel_officers:
                if(i.member.position.is_core_volunteer):
                    core_volunteers.append(i)
                else:
                    team_volunteers.append(i)
            
            context={
                'page_title':'Volunteers of IEEE NSU Student Branch',
                'core_volunteers':core_volunteers,
                'team_volunteers':team_volunteers,
                'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            }
        return render(request,'Members/Volunteers/volunteers_page.html',context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def exemplary_members(request):

    try:

        #loading all the teams of Branch
        branch_teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
        # get all exemplary members
        all_exemplary_members=ExemplaryMembers.objects.all().order_by('rank')
            
        context={
            'page_title':"Exemplary Members",
            'page_subtitle':"IEEE NSU Student Branch",
            'exemplary_members':all_exemplary_members,
            'branch_teams':branch_teams,

        }
        return render(request,"Members/Exemplary Members/exemplary_members.html",context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def team_intros(request,team_primary):

    try:

        #loading all the teams of Branch
        branch_teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
        # get team details
        team = PortData.get_team_details(team_primary=team_primary,request=request)
        
        team_co_ordinators=[]
        team_incharges=[]
        team_volunteers=[]

        get_team_members=PortData.get_specific_team_members_of_current_panel(request=request,team_primary=team.primary)
        if(get_team_members):
            for i in get_team_members:
                if(i.position.is_officer):
                    if(i.position.is_co_ordinator):
                        team_co_ordinators.append(i)
                    else:
                        team_incharges.append(i)
                elif(i.position.is_volunteer):
                    team_volunteers.append(i)    
        
        context={
            'page_title':team.team_name +' Team',
            'page_subtitle':"IEEE NSU Student Branch",
            'branch_teams':branch_teams,
            'team':team,
            'co_ordinators':team_co_ordinators,
            'incharges':team_incharges,
            'volunteers':team_volunteers,
        }
        return render(request,"Members/Teams/team.html",context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)



def all_members(request):

    try:

        # get all registered members of INSB
        get_all_members = userData.get_all_registered_members(request=request)
        recruitment_stat=userData.getRecruitmentStats()
        
        context={
            'page_title':"All Registered Members & Member Statistics of IEEE NSU SB",
            'members':get_all_members,
            'male_count':Members.objects.filter(gender="Male").count(),
            'female_count':Members.objects.filter(gender="Female").count(),
            'active_count':Members.objects.filter(is_active_member=True).count(),
            'inactive_count':Members.objects.filter(is_active_member=False).count(),
            'session_name':recruitment_stat[0],
            'session_recruitee':recruitment_stat[1],
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
        }
        return render(request,'Members/All Members/all_members.html',context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def member_profile(request, ieee_id):

    try:
        try:
            #loading all the teams of Branch
            branch_teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
            #get current branch position data
            member_data = MDT_DATA.get_member_data(ieee_id=ieee_id)
            #get current sc_ag position data for all sc_ag
            sc_ag_position_data = SC_AG_Members.objects.filter(member=ieee_id).order_by('sc_ag__primary')

            #get previous branch position data
            branch_prev_position_data = PortData.get_branch_previous_position_data(ieee_id)
            #get previous sc_ag position data for all sc_ag
            sc_ag_previous_position_data = PortData.get_sc_ag_previous_position_data(request,ieee_id)

            has_branch_prev_position=False
            if branch_prev_position_data.count() > 0:
                has_branch_prev_position = True

            has_current_branch_position = True
            #if there is no current position but there is a previous position then don't display text
            #otherwise show it
            if has_branch_prev_position and member_data.team is None:
                has_current_branch_position = False

            context = {
                'page_title':'Member Profile',
                'page_subtitle': member_data.name,
                'branch_teams': branch_teams,
                'member':member_data,
                'sc_ag_position_data':sc_ag_position_data,
                'media_url':settings.MEDIA_URL,
                'has_branch_current_position':has_current_branch_position,
                'has_branch_prev_position':has_branch_prev_position,
                'branch_prev_positions':branch_prev_position_data,
                'sc_ag_prev_positions':sc_ag_previous_position_data,
            }

            return render(request, 'Members/Profile/member_profile.html', context)
        except:
            return redirect('main_website:all_members')
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def ieee_bd_section(request):

    try:
        #loading all the teams of Branch
        branch_teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
        ieee_bangladesh_section = IEEE_Bangladesh_Section.objects.get(id=1)
        page_links = Branch.get_about_page_links(page_title='ieee_bangladesh_section')
        #getting all ieee bangladesh section gallery images
        all_images = Branch.get_all_ieee_bangladesh_section_images()

        context = {
            'is_live':True, #This enables the header and footer of the page along with wavy
            'page_title':'About - IEEE Bangladesh Section',
            'branch_teams':branch_teams,
            'ieee_bangladesh_section':ieee_bangladesh_section,
            'media_url':settings.MEDIA_URL,
            'page_links':page_links,
            'all_images':all_images,
        }
        return render(request, 'About/IEEE_bangladesh_section.html', context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def ieee_nsu_student_branch(request):

    try:
        #loading all the teams of Branch
        branch_teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
        about_ieee_nsu_student_branch = IEEE_NSU_Student_Branch.objects.get(id=1)
        date_and_event = HomepageItems.get_event_for_calender(request,1)

        context = {
            'is_live':True, #This enables the header and footer of the page along with wavy
            'page_title':'About - IEEE NSU Student Branch',
            'branch_teams':branch_teams,
            'ieee_nsu_student_branch':about_ieee_nsu_student_branch,
            'date_and_event':date_and_event,
            'media_url':settings.MEDIA_URL,
        }

        return render(request, 'About/IEEE_NSU_student_branch.html', context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def ieee_region_10(request):

    try:
        #loading all the teams of Branch
        branch_teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
        about_ieee_region_10 = IEEE_Region_10.objects.get(id=1)
        page_links = Branch.get_about_page_links(page_title='ieee_region_10')

        context = {
            'is_live':True, #This enables the header and footer of the page along with wavy
            'page_title':'About - IEEE Region 10',
            'branch_teams':branch_teams,
            'ieee_region_10':about_ieee_region_10,
            'media_url':settings.MEDIA_URL,
            'page_links':page_links
        }

        return render(request, 'About/IEEE_region_10.html', context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def ieee(request):

    try:

        #loading all the teams of Branch
        branch_teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
        about_ieee = About_IEEE.objects.get(id=1)
        page_links = Branch.get_about_page_links(page_title='about_ieee')
        
        context = {
            'is_live':True, #This enables the header and footer of the page along with wavy
            'page_title':'About - IEEE',
            'branch_teams':branch_teams,
            'about_ieee':about_ieee,
            'media_url':settings.MEDIA_URL,
            'page_links':page_links
        }

        return render(request, 'About/About_IEEE.html', context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def faq(request):

    try:
        #loading all the teams of Branch
        branch_teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
        
        all_categories = Branch.get_all_category_of_questions()
        saved_question_answers = Branch.get_saved_questions_and_answers()

        if request.method == "POST":
                #when user hits submit button on main page
                if request.POST.get('submit'):
                    #getting the user's details
                    name = request.POST.get('user_name')
                    email = request.POST.get('user_email')
                    message = request.POST.get('user_message')
                    #passing them as arguments to the function to save the data
                    if HomepageItems.save_feedback_information(request,1,name,email,message):
                        messages.success(request,"You have reached us! Thanks for your feedback")  
                    else:
                        messages.error(request,"Sorry! Try to contact us later") 
                    return redirect("main_website:faq")

        context = {
            'is_live':True,
            'all_categories':all_categories,
            'saved_question_answer':saved_question_answers,
            'page_title':'FAQ',
            'branch_teams':branch_teams,

        }

        return render(request, 'About/faq.html',context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def contact(request):

    try:

        #loading all the teams of Branch
        branch_teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)

        if request.method == "POST":
                #when user hits submit button on main page
                if request.POST.get('submit'):
                    #getting the user's details
                    name = request.POST.get('user_name')
                    email = request.POST.get('user_email')
                    message = request.POST.get('user_message')
                    #passing them as arguments to the function to save the data
                    if HomepageItems.save_feedback_information(request,1,name,email,message):
                        messages.success(request,"You have reached us! Thanks for your feedback")  
                    else:
                        messages.error(request,"Sorry! Try to contact us later") 
                    return redirect("main_website:contact")

        context = {
            'page_title':'Contact',
            'branch_teams':branch_teams
        }

        return render(request, 'Contact/contact.html', context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def toolkit(request):

    try:

        #loading all the teams of Branch
        branch_teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
        
        # load all toolkit items
        toolkit_items = Toolkit.objects.all().order_by('pk')
        
        context={
            'page_title':"Toolkit",
            'branch_teams':branch_teams,
            'all_toolkits':toolkit_items,
        }
        return render(request, 'Publications/Toolkit/toolkit.html',context=context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

def join_insb(request):

    try:

        #loading all the teams of Branch
        branch_teams = PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
        context={
                'page_title':"Join IEEE NSU SB",
                'branch_teams':branch_teams,
            }
    
        return render(request,"Get Involved/Join INSB/join_INSB.html",context=context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

    
def mega_event_description_page(request,mega_event_id):
        
    try:
        mega_event = HomepageItems.get_mega_event(mega_event_id)
        if(mega_event==False):
            return cv.custom_404(request)
        else:
            if(mega_event.publish_mega_event):
                all_events_of_mega_events = HomepageItems.all_events_of_mega_event(mega_event)
                other_mega_event =  HomepageItems.get_other_mega_event(mega_event_id)
            
                context={
                    'page_title':mega_event.super_event_name,
                    'page_subtitle':mega_event.mega_event_of,
                    'mega_event':mega_event,
                    'media_url':settings.MEDIA_URL,
                    'all_events_of_mega_event':all_events_of_mega_events,
                    'other_mega_event':other_mega_event,
                    'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
                }

                return render(request, 'Events/mega_event_description_page.html',context)
            else:
                return cv.custom_404(request)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    
def sc_ag_current_panel_members(request,sc_ag_primary):
    
    # get sc ag
    sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)
    
    # get all the panels of sc ag
    get_all_panels=Panels.objects.filter(panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).order_by('-year')

    # get current panel of sc ag
    current_panel=PortData.get_sc_ag_current_panel(request=request,sc_ag_primary=sc_ag_primary)
    
    context={
        'has_current_panel':True,
        'sc_ag':sc_ag,
        'page_title':"Current Executive Committee",
        'page_subtitle':sc_ag.group_name,
        'panels':get_all_panels,
        'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
        
    }
    if(current_panel is not None):
        get_current_panel_members=PanelMembersData.get_sc_ag_members_from_current_panel(request,sc_ag_primary=sc_ag_primary)

        if get_current_panel_members is not None:
            sc_ag_faculty_members=[]
            sc_ag_chair=[]
            sc_ag_eb_members=[]
            sc_ag_officer_members=[]
            sc_ag_volunteer_members=[]
            
            for members in get_current_panel_members:
                if members.position.is_faculty:
                    sc_ag_faculty_members.append(members)
                elif members.position.is_sc_ag_eb_member:
                    if members.position.role=="Chair":
                        sc_ag_chair.append(members)
                    else:
                        sc_ag_eb_members.append(members)
                elif members.position.is_officer:
                    sc_ag_officer_members.append(members)
                elif members.position.is_volunteer:
                    sc_ag_volunteer_members.append(members)
            
            has_faculty_members=False
            has_chair=False
            has_eb_members=False
            has_officer_member=False
            has_volunteer_member=False
            
            if(len(sc_ag_faculty_members)>0):
                has_faculty_members=True
            if(len(sc_ag_chair)>0):
                has_chair=True
            if(len(sc_ag_eb_members)>0):
                has_eb_members=True
            if(len(sc_ag_officer_members)>0):
                has_officer_member=True
            if(len(sc_ag_volunteer_members)>0):
                has_volunteer_member=True
            
            context['has_sc_ag_faculty_advisor']=has_faculty_members
            context['has_branch_chair']=has_chair
            context['has_branch_eb']=has_eb_members
            context['has_officer_member']=has_officer_member
            context['has_volunteer_member']=has_volunteer_member
            
            context['sc_ag_faculty_advisors']=sc_ag_faculty_members
            context['chair']=sc_ag_chair
            context['eb']=sc_ag_eb_members
            context['officer_member']=sc_ag_officer_members
            context['volunteer_members']=sc_ag_volunteer_members
          
    else:
        get_the_latest_panel=Panels.objects.filter(panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).order_by('-year').first()
        return redirect('main_website:sc_ag_panel_members',sc_ag_primary,get_the_latest_panel.pk,get_the_latest_panel.year)

    return render(request,"Members/Panel/SC_AG/sc_ag_panel_members.html",context=context)


def sc_ag_panel_members(request,sc_ag_primary,panel_pk,panel_year):
    
    # get sc ag
    sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)
    
    # get all the panels of sc ag
    get_all_panels=Panels.objects.filter(panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).order_by('-year')


    # get the panel
    get_panel=Panels.objects.get(pk=panel_pk)
    
    # get panel_members
    get_panel_members=PanelMembersData.get_sc_ag_members_from_panel(request,panel_pk)
    
    
    context={
        'page_title':f"Executive Panel: {panel_year}",
        'page_subtitle':sc_ag.group_name,
        'has_current_panel':True,
        'sc_ag':sc_ag,
        'panels':get_all_panels,
        'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
    }
    
    if get_panel_members is not None:
        sc_ag_faculty_members=[]
        sc_ag_chair=[]
        sc_ag_eb_members=[]
        sc_ag_officer_members=[]
        sc_ag_volunteer_members=[]
        
        for members in get_panel_members:
            if members.position.is_faculty:
                sc_ag_faculty_members.append(members)
            elif members.position.is_sc_ag_eb_member:
                if members.position.role=="Chair":
                    sc_ag_chair.append(members)
                else:
                    sc_ag_eb_members.append(members)
            elif members.position.is_officer:
                sc_ag_officer_members.append(members)
            elif members.position.is_volunteer:
                sc_ag_volunteer_members.append(members)
        
        has_faculty_members=False
        has_chair=False
        has_eb_members=False
        has_officer_member=False
        has_volunteer_member=False
        
        if(len(sc_ag_faculty_members)>0):
            has_faculty_members=True
        if(len(sc_ag_chair)>0):
            has_chair=True
        if(len(sc_ag_eb_members)>0):
            has_eb_members=True
        if(len(sc_ag_officer_members)>0):
            has_officer_member=True
        if(len(sc_ag_volunteer_members)>0):
            has_volunteer_member=True
            
        context['has_sc_ag_faculty_advisor']=has_faculty_members
        context['has_branch_chair']=has_chair
        context['has_branch_eb']=has_eb_members
        context['has_officer_member']=has_officer_member
        context['has_volunteer_member']=has_volunteer_member
        
        context['sc_ag_faculty_advisors']=sc_ag_faculty_members
        context['chair']=sc_ag_chair
        context['eb']=sc_ag_eb_members
        context['officer_member']=sc_ag_officer_members
        context['volunteer_members']=sc_ag_volunteer_members
    
    
    return render(request,"Members/Panel/SC_AG/sc_ag_panel_members.html",context=context)
def update_count_down(request):
        if request.method == 'POST':
        # Handle the POST request data
            key = request.POST.get('key')
            
            if key == "launch":
                change = system.objects.first()
                change.count_down = None
                change.save()

            return JsonResponse({'status': 'success'})