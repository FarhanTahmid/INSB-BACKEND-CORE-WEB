from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from central_branch.renderData import Branch

from central_branch.view_access import Branch_View_Access
from events import renderData
from events.models import Event_Venue, Events, SuperEvents
from django.contrib import messages

from events_and_management_team.renderData import Events_And_Management_Team

# Create your views here.

@login_required
def event_control_homepage(request):
    # This function loads all events and super events in the event homepage table
    
    has_access_to_create_event=Branch_View_Access.get_create_event_access(request=request)
    all_insb_events=Branch.load_all_events()
    context={
        'events':all_insb_events,
        'has_access_to_create_event':has_access_to_create_event,
    }
    if(request.method=="POST"):
        if request.POST.get('create_new_event'):
            print("Create")
    
    return render(request,'Events/event_homepage.html',context)

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
            return redirect('events:event_control')
        
        elif (request.POST.get('cancel')):
            return redirect('events:event_control')
        
    return render(request,"Events/Super Event/super_event_creation_form.html")


@login_required
def event_creation_form_page(request):
    
    #######load data to show in the form boxes#########
    
    #loading super/mother event at first
    super_events=Branch.load_all_mother_events()
    # event_types=Branch.load_all_event_type()

    
    context={
        'super_events':super_events,
        # 'event_types':event_types,
    }
    
    
    if(request.method=="POST"):
        if(request.POST.get('next')):
            super_event_name=request.POST.get('super_event')
            event_name=request.POST['event_name']
            event_description=request.POST['event_description']
            event_type = request.POST['event_type']
            event_date=request.POST['event_date']
    
            
            get_event=renderData.register_event_page1(
                super_event_name=super_event_name,
                event_name=event_name,
                event_type=event_type,
                event_description=event_description,
                event_date=event_date
            )
            
            if(get_event)==False:
                messages.info(request,"Database Error Occured! Please try again later.")
            else:
                #if the method returns true, it will redirect to the new page
                return redirect('central_branch:event_creation_form2',get_event)

        elif(request.POST.get('cancel')):
            return redirect('central_branch:event_control')
    return render(request,'Events/event_creation_form.html',context)

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
            
            if(renderData.register_event_page2(
                inter_branch_collaboration_list=inter_branch_collaboration_list,
                intra_branch_collaboration=intra_branch_collaboration,
                event_id=event_id)):
                return redirect('central_branch:event_creation_form3',event_id)
            else:
                messages.info(request,"Database Error Occured! Please try again later.")

        elif(request.POST.get('cancel')):
            return redirect('central_branch:event_control')


    return render(request,'Events/event_creation_form2.html',context)

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
        if request.POST.get('create_event'):
            #getting the venues for the event
            venue_list_for_event=request.POST.getlist('event_venues')
            #getting the permission criterias for the event
            permission_criterias_list_for_event=request.POST.getlist('permission_criteria')
            
            #updating data collected from part3 for the event
            update_event_details=renderData.register_event_page3(venue_list=venue_list_for_event,permission_criteria_list=permission_criterias_list_for_event,event_id=event_id)
            #if return value is false show an error message
            if(update_event_details==False):
                messages.info(request, "An error Occured! Please Try again!")
            else:
                return redirect('central_branch:event_control')

    return render(request,'Events/event_creation_form3.html',context)

@login_required
def event_description(request,event_id):

    '''Checking to see whether the user has access to view events on portal and edit them'''
    user = request.user
    has_access = Branch.event_page_access(user)
    if has_access:

        '''Details page for registered events'''

        # Get collaboration details
        interBranchCollaborations=Branch.event_interBranch_Collaborations(event_id=event_id)
        intraBranchCollaborations=Branch.event_IntraBranch_Collaborations(event_id=event_id)
        # Checking if event has collaborations
        hasCollaboration=False
        if(len(interBranchCollaborations)>0 and len(intraBranchCollaborations)>0):
            hasCollaboration=True
        
        

        get_all_team_name = Branch.load_teams()
        get_event_details = Events.objects.get(id = event_id)

        #print(get_event_details.super_event_name.id)
        get_event_venue = Event_Venue.objects.filter(event_id = get_event_details.id)  
        
        if request.method == "POST":
            #FOR TASK ASSIGNING
            team_under = request.POST.get('team')
            team_member = request.POST.get('team_member')
            probable_date = request.POST.get('probable_date')
            progress = request.POST.get('progression')    
        context={
            'event_details':get_event_details,
            'event_venue':get_event_venue,
            'team_names':get_all_team_name,
            'interBranchCollaborations':interBranchCollaborations,
            'intraBranchCollaborations':intraBranchCollaborations,
            'hasCollaboration':hasCollaboration,
        }
    else:
        return redirect('main_website:all-events')
    return render(request,"Events/event_description.html",context)

@login_required
def get_updated_options_for_event_dashboard(request):
    #this function updates the select box upon the selection of the team in task assignation. takes event id as parameter. from html file, a script hits the api and fetches the returned dictionary
    
    if request.method == 'GET':
        # Retrieve the selected value from the query parameters
        selected_team = request.GET.get('team_id')

        # fetching the team member
        members=Branch.load_team_members(selected_team)
        updated_options = [
            # Add more options as needed
        ]
        for member in members:
            updated_options.append({'value': member.ieee_id, 'member_name': member.name,'position':member.position.role})

        #returning the dictionary
        return JsonResponse(updated_options, safe=False)