from django.shortcuts import render
from django.http import HttpResponse
from central_branch.models import Events
from central_branch.renderData import Branch
from main_website.models import Research_Papers,Blog


# Create your views here.
def index(request):
    return HttpResponse("IEEE main Website")

def All_Events(request):

    '''Loads all events up untill today on Event page'''


    get_all_events = Branch.load_all_events()
    return render(request,"All_Events.html",{
        "events":get_all_events,
        "last_event":get_all_events.last()
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