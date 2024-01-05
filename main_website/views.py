from django.shortcuts import render,redirect
from django.http import HttpResponse
from central_events.models import Events
from central_branch.renderData import Branch
from main_website.models import Research_Papers,Blog,Achievements,News
from port.renderData import PortData
from port.models import Teams,Panels,Chapters_Society_and_Affinity_Groups
from .renderData import HomepageItems
from django.conf import settings
from users.models import User_IP_Address,Members
from users.models import User_IP_Address
import logging
from datetime import datetime
from django.http import HttpResponseBadRequest,HttpResponseServerError
from system_administration.system_error_handling import ErrorHandling
import traceback
from .renderData import HomepageItems
from users.renderData import PanelMembersData
from users import renderData as userData
import json,requests
from insb_port import settings
from .models import *

logger=logging.getLogger(__name__)

# Create your views here.
def homepage(request):
    bannerItems=HomepageItems.getHomepageBannerItems()
    bannerWithStat=HomepageItems.getBannerPictureWithStat()
    HomepageItems.get_ip_address(request)
    
    
    # get recent 6 news
    get_recent_news=News.objects.filter().order_by('-news_date')[:6]
    # get recent 6 Blogs
    get_recent_blogs=Blog.objects.filter(publish_blog=True).order_by('-date')[:6]
    context={
        'banner_item':bannerItems,
        'banner_pic_with_stat':bannerWithStat,
        'media_url':settings.MEDIA_URL,
        'all_member_count':HomepageItems.getAllIEEEMemberCount(),
        'event_count':HomepageItems.getEventCount(),
        'recent_news':get_recent_news,
        'recent_blogs':get_recent_blogs,
        'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
    }
    return render(request,"LandingPage/homepage.html",context)


##################### EVENT WORKS ####################

# def all_events(request):

#     '''Loads all events up untill today on Event page'''
#     get_all_events = Branch.load_all_events()

#     '''Fetching 6 events among which atleast 2 are flagship events.
#        If no flagship event exists then all are normal events'''
#     count = 0
#     get_flagship_event = Events.objects.filter(Q(flagship_event = True) & Q(publish_in_main_web= True)).order_by('-probable_date')[:6]
#     count += len(get_flagship_event)
#     get_event = Events.objects.filter(Q(flagship_event = False) & Q(publish_in_main_web= True)).order_by('-probable_date')[:(6-count)]
    
#     context={
#         "events":get_all_events,
#         "last_event":get_all_events.last(),
#         "flagship_event":get_flagship_event,
#         "normal_event":get_event,
#     }
#     return render(request,"Events/events_homepage.html",context)


def event_homepage(request):

    '''This view function loads all the events for the events homepage'''
    
    try:
        all_events = HomepageItems.load_all_events(True)
        latest_five_events = HomepageItems.load_all_events(False)
        date_and_event = HomepageItems.get_event_for_calender()
        upcoming_event = HomepageItems.get_upcoming_event()
        upcoming_event_banner_picture = HomepageItems.get_upcoming_event_banner_picture(upcoming_event)


        context = {
            'page_title':"Events - IEEE NSU Student Branch",
            'all_events':all_events,
            'media_url':settings.MEDIA_URL,
            'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
            'latest_five_event':latest_five_events,
            'date_and_event':date_and_event,
            'upcoming_event':upcoming_event,
            'upcoming_event_banner_picture':upcoming_event_banner_picture,
        }

        return render(request,'Events/events_homepage.html',context)
    except Exception as e:
            print(e)
            response = HttpResponseServerError("Oops! Something went wrong.")
            return response
    
    
def event_details(request,event_id):
 
    '''Loads details for the corresponding event page on site'''
    try:
        get_event = Events.objects.get(id = event_id)
        if(get_event.publish_in_main_web):
            event_banner_image = HomepageItems.load_event_banner_image(event_id=event_id)
            event_gallery_images = HomepageItems.load_event_gallery_images(event_id=event_id)

            return render(request,"Events/event_description_main.html",{
                "event":get_event,
                'media_url':settings.MEDIA_URL,
                'event_banner_image' : event_banner_image,
                'event_gallery_images' : event_gallery_images
            })
        else:
            return redirect('main_website:event_homepage')
    except:
        return redirect('main_website:event_homepage')



# ###################### ACHIEVEMENTS ##############################

def achievements(request):
    # load achievement of INSB
    load_all_achievements=Achievements.objects.all().order_by('-award_winning_year')
    context={
        'page_title':"Achievements",
        'achievements':load_all_achievements,
        'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch

    }
    
    return render(request,"Activities/achievements.html",context=context)

def news(request):
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

    

######################SC_AG############################################
def rasPage(request):

    society = Chapters_Society_and_Affinity_Groups.objects.get(primary = 3)
        
    featured_events = HomepageItems.get_featured_events_for_societies(3)
    # getRasAbout=society_ag.Ras.get_ras_about()
        
    # if getRasAbout is False:
    #     return HttpResponse("GG")
        
    context={
            
        'society':society,
        #'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
        'media_url':settings.MEDIA_URL,
        'featured_events':featured_events

    }
    return render(request,'Society_AG/sc_ag.html',context=context)
def pesPage(request):

    society = Chapters_Society_and_Affinity_Groups.objects.get(primary = 2)
        
    featured_events = HomepageItems.get_featured_events_for_societies(2)
            
    context={
            
        'society':society,
        #'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
        'media_url':settings.MEDIA_URL,
        'featured_events':featured_events

    }
    return render(request,'Society_AG/sc_ag.html',context=context)
def iasPage(request):

    society = Chapters_Society_and_Affinity_Groups.objects.get(primary = 4)
        
    featured_events = HomepageItems.get_featured_events_for_societies(4)
            

        
    context={
            
        'society':society,
        #'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
        'media_url':settings.MEDIA_URL,
        'featured_events':featured_events

    }
    return render(request,'Society_AG/sc_ag.html',context=context)
def wiePage(request):

    society = Chapters_Society_and_Affinity_Groups.objects.get(primary = 5)
        
    featured_events = HomepageItems.get_featured_events_for_societies(5)
            
        
    context={
            
        'society':society,
        #'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
        'media_url':settings.MEDIA_URL,
        'featured_events':featured_events

    }
    return render(request,'Society_AG/sc_ag.html',context=context)



######################## BLOG WORKS ################################


def blogs(request):

    '''Loads the blog page where all blog is shown'''

    get_all_blog= Blog.objects.filter(publish_blog=True)
    context={
        'page_title':"Blogs",
        'blogs':get_all_blog,
        'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
    }
    return render(request,"Publications/Blog/blog.html",context=context)

def blog_Description(request,blog_id):
    load_specific_blog = Blog.objects.get(id=blog_id)
    return render(request,"Blog_Details.html",{
        "blog_details":load_specific_blog
    })


######################### RESEARCH PAPER WORKS ###########################

def Research_Paper(request):

    '''Loads all research papers for the corresponding page'''


    get_all_research_papers = Research_Papers.objects.all() 
    return render(request,"All_Research_Papers.html",{
        "research_paper":get_all_research_papers
    })

######################### Magazine WORKS ###########################

def magazines(request):
    '''Loads all the magazines for the corresponding page'''
    get_all_magazines=Magazines.objects.all().order_by('-publish_date')
    context={
        'page_title':"Magazines",
        'all_magazines':get_all_magazines,
    }
    return render(request,"Publications/Magazines/magazine.html",context=context)

######################### GALLERY WORKS ###########################
def gallery(request):
    return render(request, 'gallery.html')


# Memeber works

def current_panel_members(request):
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
        sc_ag_faculty_advisors=[]
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

def panel_members_page(request,year):
    get_all_panels=Branch.load_all_panels()
    get_panel=Branch.get_panel_by_year(year)
    get_panel_members=Branch.load_panel_members_by_panel_id(panel_id=get_panel.pk)
    # TODO:add algo to add SC AG Faculty and EB
    branch_counselor=[]
    sc_ag_faculty_advisors=[]
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
        'page_title':f"Executive Panel - {year}"
    }
    return render(request,'Members/Panel/panel_members.html',context)

def officers_page(request):
    # get all teams of IEEE NSU Student Branch
    get_teams=PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1)
    # get all officers of branch. to get the current officers load the current panel of branch
    get_current_panel=Branch.load_current_panel()
    if(get_current_panel is None):
        # there is no current panel, so there will be no officer, so pass just the team contexts.
        context={
        'page_title':'Officers of IEEE NSU Student Branch',
        'teams':get_teams,
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

def team_based_officers_page(request,team_primary):
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

def volunteers_page(request):
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


def team_intros(request,team_primary):
    
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
        'team':team,
        'co_ordinators':team_co_ordinators,
        'incharges':team_incharges,
        'volunteers':team_volunteers,
    }
    return render(request,"Members/Teams/team.html",context=context)



def all_members(request):
    # get all registered members of INSB
    get_all_members = userData.get_all_registered_members(request=request)
    recruitment_stat=userData.getRecruitmentStats()
    
    
    context={
        'page_title':"All Registered Members & Member Statistics of IEEE NSU SB",
        'members':get_all_members,
        'male_count':Members.objects.filter(gender="Male").count(),
        'female_count':Members.objects.filter(gender="Female").count(),
        'session_name':recruitment_stat[0],
        'session_recruitee':recruitment_stat[1],
        'branch_teams':PortData.get_teams_of_sc_ag_with_id(request=request,sc_ag_primary=1), #loading all the teams of Branch
    }
    return render(request,'Members/All Members/all_members.html',context=context)

def member_profile(request):
    return render(request, 'Members/Profile/member_profile.html')

def ieee_bd_section(request):
    return render(request, 'About/IEEE_bangladesh_section.html')

def ieee_nsu_student_branch(request):
    return render(request, 'About/IEEE_NSU_student_branch.html')

def ieee_region_10(request):
    # template not done yet
    return render(request, 'About/IEEE_region_10.html')

def ieee(request):
    return render(request, 'About/About_IEEE.html')

def faq(request):
    return render(request, 'About/faq.html')

def contact(request):
    return render(request, 'Contact/contact.html')
