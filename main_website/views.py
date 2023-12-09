from django.shortcuts import render
from django.http import HttpResponse
from central_events.models import Events
from central_branch.renderData import Branch
from main_website.models import Research_Papers,Blog
from django.db.models import Q
from .renderData import HomepageItems
from django.conf import settings
from users.models import User
import logging
from datetime import datetime
from django.http import HttpResponseBadRequest,HttpResponseServerError
from system_administration.system_error_handling import ErrorHandling
import traceback
from .renderData import HomepageItems


logger=logging.getLogger(__name__)

# Create your views here.
def homepage(request):
    bannerItems=HomepageItems.getHomepageBannerItems()
    bannerWithStat=HomepageItems.getBannerPictureWithStat()
    context={
        'banner_item':bannerItems,
        'banner_pic_with_stat':bannerWithStat,
        'media_url':settings.MEDIA_URL,
        'all_member_count':HomepageItems.getAllIEEEMemberCount(),
        'event_count':HomepageItems.getEventCount(),
    }
    return render(request,"LandingPage/homepage.html",context)

def index(request):

    def get_ip_address(request):
        address = request.META.get('HTTP_X_FORWARDED_FOR')
        if address:
            ip = address.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    ip = get_ip_address(request)
    user =User(ip_address = ip)
    print(f"Current user ip address {user}")
    result = User.objects.filter(ip_address = ip)
    print(f"User exists in database {result}")
    if len(result)>=1:
        pass
    else:
        user.save()

    return HttpResponse("IEEE main Website")


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
        all_events = HomepageItems.load_all_events()


        context = {
            'all_events':all_events,
            'media_url':settings.MEDIA_URL,
        }

        return render(request,'Events/events_homepage.html',context)
    except Exception as e:
            print(e)
            response = HttpResponseServerError("Oops! Something went wrong.")
            return response
    


def Event_Details(request,event_id):
 
    '''Loads details for the corresponding event page on site'''
    get_event = Events.objects.get(id = event_id)
    get_event=[]
    return render(request,"Event.html",{
        "event":get_event
        
    })


# ###################### ACHIEVEMENTS ##############################

def achievements(request):
    return render(request,"Activities/achievements.html")

    

######################### SOCIETY & AG WORKS #######################
from . import society_ag
def rasPage(request):
    # Title of the page
    page_title="IEEE NSU RAS Student Branch Chapter"
    # Second para after the title
    secondary_para="Focusing on the research, study, and exchange of knowledge regarding Robotics & Automation."
    
    getRasAbout=society_ag.Ras.get_ras_about()
    
    if getRasAbout is False:
        return HttpResponse("GG")
    
    context={
        'page_title':page_title,
        'secondary_para':secondary_para,
        'about_ras':getRasAbout,
    }
    return render(request,'Society_AG/ras.html',context=context)



######################## BLOG WORKS ################################


def Blogs(request):

    '''Loads the blog page where all blog is shown'''

    get_all_blog= Blog.objects.all()
    context={
        'blogs':get_all_blog,
    }
    return render(request,"blogs.html",context=context)

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
    

# Memeber works

def current_panel_members(request):
    # load all panels at first
    get_all_panels=Branch.load_all_panels()
    get_current_panel=Branch.load_current_panel()
    get_current_panel_members=Branch.load_panel_members_by_panel_id(panel_id=get_current_panel.pk)
    
        # TODO:add algo to add SC AG Faculty and EB

    branch_counselor=[]
    sc_ag_faculty_advisors=[]
    mentors=[]
    branch_chair=[]
    branch_eb=[]
    sc_ag_chair=[]
    
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
        'panels':get_all_panels,
        'branch_counselor':branch_counselor,
        'sc_ag_faculty_advisors':sc_ag_faculty_advisors,
        'mentors':mentors,
        'chair':branch_chair,
        'eb':branch_eb,
        'sc_ag_chair':sc_ag_chair
    }
    
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
    sc_ag_chair=[]
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
        'sc_ag_chair':sc_ag_chair
    }
    return render(request,'Members/Panel/panel_members.html',context)