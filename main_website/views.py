from django.shortcuts import render
from django.http import HttpResponse
from central_branch.models import Events
from central_branch.renderData import Branch
from main_website.models import Research_Papers,Blog
from django.db.models import Q
from users.models import User

# Create your views here.
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
    result = User.objects.filter(ip_address = ip)
    if len(result)>=1:
        pass
    else:
        user.save()

    return HttpResponse("IEEE main Website")

def All_Events(request):

    '''Loads all events up untill today on Event page'''
    get_all_events = Branch.load_all_events()

    '''Fetching 6 events among which atleast 2 are flagship events.
       If no flagship event exists then all are normal events'''
    count = 0
    get_flagship_event = Events.objects.filter(Q(flagship_event = True) & Q(publish_in_main_web= True)).order_by('-probable_date')[:6]
    count += len(get_flagship_event)
    get_event = Events.objects.filter(Q(flagship_event = False) & Q(publish_in_main_web= True)).order_by('-probable_date')[:(6-count)]
    
    return render(request,"All_Events.html",{
        "events":get_all_events,
        "last_event":get_all_events.last(),
        "flagship_event":get_flagship_event,
        "normal_event":get_event

    })

def Event_Details(request,event_id):

 
    '''Loads details for the corresponding event page on site'''
    get_event = Events.objects.get(id = event_id)
    return render(request,"Event.html",{
        "event":get_event
        
    })

def Research_Paper(request):

    '''Loads all research papers for the corresponding page'''


    get_all_research_papers = Research_Papers.objects.all() 
    return render(request,"All_Research_Papers.html",{
        "research_paper":get_all_research_papers
    })

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
