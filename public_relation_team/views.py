from django.shortcuts import render,redirect
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from central_branch import renderData
from django.contrib.auth.decorators import login_required
from central_branch.models import SuperEvents,Events
from central_branch.renderData import Branch
from django.contrib import messages
from events_and_management_team.renderData import Events_And_Management_Team
from .renderData import PRT_Data



# Create your views here.

def team_home_page(request):
    return render(request,"public_relation_team/team_homepage.html")

@login_required
def event_control(request):
    all_insb_events=renderData.Branch.load_all_events()
    context={
        'events':all_insb_events,
    }
    if(request.method=="POST"):
        if request.POST.get('create_new_event'):
            print("Create")
    
    return render(request,'public_relation_team/event/event_page.html',context)

@login_required
def super_event_creation(request):

    '''function for creating super event'''

    if request.method == "POST":

        '''Checking to see if either of the submit or cancelled button has been clicked'''

        if (request.POST.get('Submit')):

            '''Getting data from page and saving them in database'''

            super_event_name = request.POST.get('super_event_name')
            super_event_description = request.POST.get('super_event_description')
            start_date = request.POST.get('probable_date')
            end_date = request.POST.get('final_date')
            saving_data = SuperEvents(super_event_name=super_event_name,super_event_description=super_event_description,start_date=start_date,end_date=end_date)
            saving_data.save()
            return redirect('public_relation_team:event_control')
        
        elif (request.POST.get('cancel')):
            return redirect('public_relation_team:event_control')
        
    return render(request,"public_relation_team/event/super_event_creation_form.html")
@login_required
def event_creation_form_page1(request):
    
    #######load data to show in the form boxes#########
    
    #loading super/mother event at first
    super_events=Branch.load_all_mother_events()
    event_types=Branch.load_all_event_type()

    
    context={
        'super_events':super_events,
        'event_types':event_types,
    }
    
    
    if(request.method=="POST"):
        if(request.POST.get('next')):
            super_event_name=request.POST.get('super_event')
            event_name=request.POST['event_name']
            event_description=request.POST['event_description']
            probable_date=request.POST['probable_date']
            final_date=request.POST['final_date']
            
            get_event=renderData.Branch.register_event_page1(
                super_event_name=super_event_name,
                event_name=event_name,
                event_description=event_description,
                probable_date=probable_date,
                final_date=final_date)
            
            if(get_event)==False:
                messages.info(request,"Database Error Occured! Please try again later.")
            else:
                #if the method returns true, it will redirect to the new page
                return redirect('public_relation_team:event_creation_form2',get_event)


                
            
                
        elif(request.POST.get('cancel')):
            return redirect('public_relation_team:event_control')
    return render(request,'public_relation_team/event/event_creation_form1.html',context)

@login_required
def event_creation_form_page2(request,event_id):
    #loading all inter branch collaboration Options
    inter_branch_collaboration_options=Branch.load_all_inter_branch_collaboration_options()
    context={
        'inter_branch_collaboration_options':inter_branch_collaboration_options,
    }
    if request.method=="POST":
        if(request.POST.get('next')):
            inter_branch_collaboration_list=request.POST.getlist('inter_branch_collaboration')
            intra_branch_collaboration=request.POST['intra_branch_collaboration']
            
            if(renderData.Branch.register_event_page2(
                inter_branch_collaboration_list=inter_branch_collaboration_list,
                intra_branch_collaboration=intra_branch_collaboration,
                event_id=event_id)):
                return redirect('public_relation_team:event_creation_form3',event_id)
            else:
                messages.info(request,"Database Error Occured! Please try again later.")

        elif(request.POST.get('cancel')):
            return redirect('public_relation_team:event_control')


    return render(request,'public_relation_team/event/event_creation_form2.html',context)

def event_creation_form_page3(request,event_id):
    #loading all venues from the venue list from event management team database
    venues=Events_And_Management_Team.getVenues()
    #loading all the permission criterias from event management team database
    permission_criterias=Events_And_Management_Team.getPermissionCriterias()

    context={
        'venues':venues,
        'permission_criterias':permission_criterias,
    }
    if request.method=="POST":
        if request.POST.get('next'):
            #getting the venues for the event
            venue_list_for_event=request.POST.getlist('event_venues')
            #getting the permission criterias for the event
            permission_criterias_list_for_event=request.POST.getlist('permission_criteria')
            
            #updating data collected from part3 for the event
            update_event_details=renderData.Branch.register_event_page3(venue_list=venue_list_for_event,permission_criteria_list=permission_criterias_list_for_event,event_id=event_id)
            #if return value is false show an error message
            if(update_event_details==False):
                messages.info(request, "An error Occured! Please Try again!")
            else:
                return redirect('public_relation_team:event_control')

    return render(request,'public_relation_team/event/event_creation_form3.html',context)

@login_required
def manage_event(request):
    all_insb_events=renderData.Branch.load_all_events()
    context={
        'events':all_insb_events,
    }
    if request.method == "POST":
        if request.POST.get('update'):
            publish_to_web = False

            #Getting values from checkbox
            if request.POST.get('publish_in_main_web'):
                publish_to_web =True
            event_id = request.POST.get('event_id')
            if PRT_Data.publish_event_to_website(publish_to_web,event_id):
                event_updated_for = Events.objects.get(id=event_id)
                messages.info(request,f"Event, {event_updated_for.event_name} has been modified on website")
            else:
                messages.info(request,f"Something Went Wrong!")

    return render(request,"public_relation_team/event/manage_event.html",context)