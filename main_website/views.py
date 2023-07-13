from django.shortcuts import render
from django.http import HttpResponse
from central_branch.models import Events,ResearchPaper,Blog
from central_branch.renderData import Branch



# Create your views here.
def index(request):
    return HttpResponse("IEEE main Website")

def All_Events(request):
    
    '''Loads all events up untill today on Event page'''

    get_all_events = Branch.load_all_events()
    return render(request,"All_Events.html",{
        "events":get_all_events,
        "Latest_event":get_all_events.last()
    })

def Event_Details(request,event_name):

    '''Loads details for the corresponding event page on site'''
   

    get_event = Events.objects.get(slug = event_name)
    return render(request,"Event.html",{
        "event":get_event
    })

def Research_Paper(request):

    '''Loads all research papers for the corresponding page'''


    get_all_research_papers = ResearchPaper.objects.all() 
    return render(request,"All_Research_Papers.html",{
        "rpaper":get_all_research_papers
    })
def Blogs(request):
    get_all_blog= Blog.objects.all()
    pic=get_all_blog.first().Blog_picture
    print(pic)
    return render(request,"Blogs.html",{
        "blogs":get_all_blog
    })