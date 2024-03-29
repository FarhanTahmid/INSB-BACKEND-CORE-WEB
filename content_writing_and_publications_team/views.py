import os
from django.http import HttpResponseBadRequest
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from central_events.forms import EventForm
from central_events.models import Events
from content_writing_and_publications_team.manage_access import CWPTeam_Render_Access
from content_writing_and_publications_team.models import Content_Team_Content, Content_Team_Content_Caption, Content_Team_Content_Document, Content_Team_Document, Content_Team_Documents_Link
from insb_port import settings
from port.renderData import PortData
from users.models import Members
from central_branch.renderData import Branch
from port.models import Roles_and_Position
from django.contrib import messages
from .renderData import ContentWritingTeam
from system_administration.models import CWP_Data_Access
from system_administration.system_error_handling import ErrorHandling
import logging
from datetime import datetime
import traceback
from .forms import Content_Form
from users.renderData import PanelMembersData,LoggedinUser,member_login_permission
from central_branch import views as cv

logger=logging.getLogger(__name__)
# Create your views here.

@login_required
@member_login_permission
def homepage(request):

    try:

        sc_ag=PortData.get_all_sc_ag(request=request)
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        # get team members
        get_officers=ContentWritingTeam.get_officers()
        get_volunteers=ContentWritingTeam.get_volunteers()
        
        context = {
            'user_data':user_data,
            'all_sc_ag':sc_ag,
            'co_ordinators':get_officers[0],
            'incharges':get_officers[1],
            'core_volunteers':get_volunteers[0],
            'team_volunteers':get_volunteers[1]
        }
        return render(request,"Homepage/content_homepage.html", context)
    
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def manage_team(request):

    '''This function loads the manage team page for content writing and publications team and is accessable
    by the co-ordinatior only, unless the co-ordinators gives access to others as well'''

    try:

        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        has_access = CWPTeam_Render_Access.access_for_manage_team(request)
        if has_access:
            data_access = ContentWritingTeam.load_manage_team_access()
            team_members = ContentWritingTeam.load_team_members()
            #load all position for insb members
            position=PortData.get_all_volunteer_position_with_sc_ag_id(request=request,sc_ag_primary=1)
            #load all insb members
            all_insb_members=Members.objects.all()
            #load all current panel members
            current_panel_members = Branch.load_current_panel_members()

            if request.method == "POST":
                if (request.POST.get('add_member_to_team')):
                    #get selected members
                    members_to_add=request.POST.getlist('member_select1')
                    #get position
                    position=request.POST.get('position')
                    for member in members_to_add:
                        ContentWritingTeam.add_member_to_team(member,position)
                        messages.success(request,f"{member} added successfully in the Team")
                    return redirect('content_writing_and_publications_team:manage_team')
                
                if (request.POST.get('remove_member')):
                    '''To remove member from team table'''
                    try:
                        current_panel=Branch.load_current_panel()
                        PanelMembersData.remove_member_from_panel(request=request,panel_id=current_panel.pk,ieee_id=request.POST['remove_ieee_id'])
                        try:
                            CWP_Data_Access.objects.filter(ieee_id=request.POST['remove_ieee_id']).delete()
                        except CWP_Data_Access.DoesNotExist:
                            return redirect('content_writing_and_publications_team:manage_team')
                        return redirect('content_writing_and_publications_team:manage_team')
                    except:
                        pass
                if request.POST.get('access_update'):
                    manage_team_access = False
                    if(request.POST.get('manage_team_access')):
                        manage_team_access=True
                    event_access=False
                    if(request.POST.get('event_access')):
                        event_access=True
                    content_access=False
                    if(request.POST.get('content_access')):
                        content_access=True
                    content_view_access=False
                    if(request.POST.get('content_view_access')):
                        content_view_access=True
                    ieee_id=request.POST['access_ieee_id']
                    if (ContentWritingTeam.cwp_manage_team_access_modifications(manage_team_access, event_access, content_access, content_view_access, ieee_id)):
                        permission_updated_for=Members.objects.get(ieee_id=ieee_id)
                        messages.info(request,f"Permission Details Was Updated for {permission_updated_for.name}")
                    else:
                        messages.info(request,f"Something Went Wrong! Please Contact System Administrator about this issue")
                
                if request.POST.get('access_remove'):
                    '''To remove record from data access table'''
                    
                    ieeeId=request.POST['access_ieee_id']
                    if(ContentWritingTeam.remove_member_from_manage_team_access(ieee_id=ieeeId)):
                        messages.info(request,"Removed member from Managing Team")
                        return redirect('content_writing_and_publications_team:manage_team')
                    else:
                        messages.info(request,"Something went wrong!")

                if request.POST.get('update_data_access_member'):
                    
                    new_data_access_member_list=request.POST.getlist('member_select')
                    
                    if(len(new_data_access_member_list)>0):
                        for ieeeID in new_data_access_member_list:
                            if(ContentWritingTeam.add_member_to_manage_team_access(ieeeID)=="exists"):
                                messages.info(request,f"The member with IEEE Id: {ieeeID} already exists in the Data Access Table")
                            elif(ContentWritingTeam.add_member_to_manage_team_access(ieeeID)==False):
                                messages.info(request,"Something Went wrong! Please try again")
                            elif(ContentWritingTeam.add_member_to_manage_team_access(ieeeID)==True):
                                messages.info(request,f"Member with {ieeeID} was added to the team table!")
                                return redirect('content_writing_and_publications_team:manage_team')

            context={
                'user_data':user_data,
                'data_access':data_access,
                'members':team_members,
                'insb_members':all_insb_members,
                'current_panel_members':current_panel_members,
                'positions':position,
                'all_sc_ag':sc_ag,
            }
            return render(request,"content_writing_and_publications_team/manage_team.html",context=context)
        else:
            return render(request,"content_writing_and_publications_team/access_denied.html", {'all_sc_ag':sc_ag,'user_data':user_data,})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def event_page(request):

    '''Only events organised by INSB would be shown on the event page of Content and Publications Team
       So, only those events are being retrieved from database'''
    try:

        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file  
        sc_ag=PortData.get_all_sc_ag(request=request)
        insb_organised_events = Branch.load_insb_organised_events()

        context = {
            'user_data':user_data,
            'events_of_insb_only':insb_organised_events,
            'all_sc_ag':sc_ag,
        }
        

        return render(request,"Events/content_team_events_homepage.html",context)
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)


@login_required
@member_login_permission
def event_form(request,event_id):

    try:
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        has_access = CWPTeam_Render_Access.access_for_events(request)

        if has_access:
            if(request.method == "POST"):
                if('save' in request.POST):
                    event_description = request.POST['event_description']
                    if('drive_link_of_documents' in request.POST):
                        drive_link = request.POST['drive_link_of_documents']
                        success = ContentWritingTeam.update_event_details(event_id=event_id, event_description=event_description, drive_link=drive_link)
                    else:
                        success = ContentWritingTeam.update_event_details(event_id=event_id, event_description=event_description)

                    if(success):
                        messages.success(request,"Event details updated successfully!")
                    else:
                        messages.error(request,"Error occured! Please try again later.")

                    if(len(request.FILES.getlist('document')) > 0):
                        file_list = request.FILES.getlist('document')
                        success2 = ContentWritingTeam.upload_files(event_id=event_id, file_list=file_list)
                        if(success2):
                            messages.success(request,"Files uploaded successfully!")
                        else:
                            messages.error(request,"Error occured while uploading files! Please try again later.")
                            
                    return redirect("content_writing_and_publications_team:event_form",event_id)
                
                if('remove' in request.POST):
                    id = request.POST.get('remove_doc')
                    if ContentWritingTeam.delete_file(id):
                        messages.success(request,"File deleted successfully!")
                    else:
                        messages.error(request,"Error occured! Please try again later.")
                    return redirect("content_writing_and_publications_team:event_form",event_id)
                
            event_details = Events.objects.get(id=event_id)
            form = EventForm({'event_description' : event_details.event_description})
            try:
                documents_link = Content_Team_Documents_Link.objects.get(event_id = Events.objects.get(pk=event_id))
            except:
                documents_link = None

            documents = Content_Team_Document.objects.filter(event_id=event_id)
            
            context = {
                'user_data':user_data,
                'all_sc_ag' : sc_ag,
                'event_id' : event_id,
                'event_details' : event_details,
                'description_form' : form,
                'drive_link_of_documents' : documents_link,
                'media_url' : settings.MEDIA_URL,
                'documents' : documents
            }

            return render(request,"Events/content_team_event_form.html", context)
        else:
            return redirect('main_website:event_details', event_id)
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)
    

@login_required
@member_login_permission
def event_form_add_notes(request,event_id):
    ''' This function is used to generate view for add notes of content team. '''

    try:
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)
        has_access = CWPTeam_Render_Access.access_for_events(request)
        if has_access:
            all_notes_content = ContentWritingTeam.load_note_content(event_id)
            form = Content_Form()
            if(request.method == "POST"):               
                if 'add_note' in request.POST:
                    
                    #when the add button for submitting new note is clicked
                    title = request.POST['title']
                    note = request.POST['caption']

                    if ContentWritingTeam.creating_note(title,note,event_id):
                        messages.success(request,"Note created successfully!")
                    else:
                        messages.error(request,"Error occured! Please try again later.")

                    return redirect("content_writing_and_publications_team:event_form_add_notes",event_id)

                if 'remove' in request.POST:
                    id = request.POST.get('remove_note')
                    if ContentWritingTeam.remove_note(id):
                        messages.success(request,"Note deleted successfully!")
                    else:
                        messages.error(request,"Error occured! Please try again later.")
                    return redirect("content_writing_and_publications_team:event_form_add_notes",event_id)  

                if 'update_note' in request.POST:
                    id = request.POST['update_note']
                    title = request.POST['title']
                    note = request.POST['caption']
                    if(ContentWritingTeam.update_note(id, title, note)):
                        messages.success(request,"Note updated successfully!")
                    else:
                        messages.error(request,"Error occured! Please try again later.")
                    return redirect("content_writing_and_publications_team:event_form_add_notes",event_id)
            
            context = {
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'event_id':event_id,
                'form_adding_note':form,
                'all_notes_content':all_notes_content,
            }

            return render(request,"Events/content_team_event_form_add_notes.html", context)
        else:
            return redirect('main_website:event_details', event_id)
        
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def content_page(request):
    try:
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        has_content_access = CWPTeam_Render_Access.access_for_content(request)
        has_access = has_content_access or CWPTeam_Render_Access.access_for_view_content(request)
        if has_access:
            all_contents = Content_Team_Content.objects.all().order_by('-pk')

            context = {
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'all_contents':all_contents,
                'has_content_access':has_content_access
            }

            return render(request,"Content/content_page.html",context)
        else:
            return render(request,"content_writing_and_publications_team/access_denied.html", {'all_sc_ag':sc_ag,'user_data':user_data})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def create_content_form(request):
    try:
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        has_access = CWPTeam_Render_Access.access_for_content(request)
        if has_access:
            if request.method == 'POST':
                title = request.POST.get('content_title')
                description = request.POST.get('content_description_details')
                documents_link = request.POST.get('drive_link_of_documents')
                documents = None
                if request.FILES.get('document'):
                    documents = request.FILES.getlist('document')

                if(ContentWritingTeam.create_content(title,description,documents_link,documents)):
                    messages.success(request, 'Content created successfully!')
                else:
                    messages.warning(request,'Something went wrong while creating the content!')

                return redirect('content_writing_and_publications_team:content_page')

            return render(request,"Content/create_content_form.html", {'user_data':user_data, 'all_sc_ag':sc_ag})
        else:
            return render(request,"content_writing_and_publications_team/access_denied.html", {'all_sc_ag':sc_ag,'user_data':user_data})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def content_edit(request, content_id):
    try:
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        has_content_access = CWPTeam_Render_Access.access_for_content(request)
        has_access = has_content_access or CWPTeam_Render_Access.access_for_view_content(request)
        if has_access:
            if request.method == 'POST' and has_content_access:
                if 'update' in request.POST:
                    title = request.POST.get('content_title')
                    description = request.POST.get('content_description_details')
                    documents_link = request.POST.get('drive_link_of_documents')

                    documents = None
                    if request.FILES.get('document'):
                        documents = request.FILES.getlist('document')

                    if ContentWritingTeam.update_content(content_id, title, description, documents_link, documents):
                        messages.success(request,'Content updated successfully!')
                    else:
                        messages.warning(request,'Something went wrong while updating the content!')
                    
                    return redirect('content_writing_and_publications_team:content_edit', content_id)   

                elif 'remove' in request.POST:
                    document_id = request.POST.get('remove_doc')

                    if(ContentWritingTeam.remove_content_doc(document_id)):
                        messages.success(request, 'Document deleted successfully!')
                    else:
                        messages.warning(request,'Something went wrong while deleting the document!')

                    return redirect('content_writing_and_publications_team:content_edit', content_id)

                elif 'delete_content' in request.POST:
                    if(ContentWritingTeam.delete_content(request,content_id)):
                        messages.success(request,'Content deleted successfully!')
                    else:
                        messages.warning(request,'Something went wrong while deleting the content')
                    
                    return redirect('content_writing_and_publications_team:content_page') 
            
            content = Content_Team_Content.objects.get(id=content_id)
            content_docs = Content_Team_Content_Document.objects.filter(content_id=content_id)

            context = {
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'content_id':content_id,
                'content':content,
                'content_docs':content_docs,
                'media_url':settings.MEDIA_URL,
                'has_content_access':has_content_access
            }

            return render(request,"Content/edit_content_form.html",context)
        else:
            return render(request,"content_writing_and_publications_team/access_denied.html", {'all_sc_ag':sc_ag,'user_data':user_data})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)

@login_required
@member_login_permission
def edit_content_form_add_notes(request, content_id):
    try:
        current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
        user_data=current_user.getUserData() #getting user data as dictionary file
        sc_ag=PortData.get_all_sc_ag(request=request)

        has_content_access = CWPTeam_Render_Access.access_for_content(request)
        has_access = has_content_access or CWPTeam_Render_Access.access_for_view_content(request)
        if has_access:
            captions = Content_Team_Content_Caption.objects.filter(content_id=content_id)

            if request.method == 'POST' and has_content_access:
                if 'add_caption' in request.POST:
                    title = request.POST.get('title')
                    caption = request.POST.get('add_content_caption_details')

                    if(ContentWritingTeam.create_content_caption(content_id, title, caption)):
                        messages.success(request,'Caption added successfully!')
                    else:
                        messages.warning(request,'Something went wrong while creating the caption!')
                
                elif 'update' in request.POST:
                    caption_id = request.POST.get('update_caption')
                    title = request.POST.get('title')
                    caption = request.POST.get(f'content_caption_details_{caption_id}')
                    
                    if(ContentWritingTeam.update_content_caption(caption_id, title, caption)):
                        messages.success(request,'Caption updated successfully!')
                    else:
                        messages.warning(request,'Something went wrong while updating the caption!')
                
                elif 'remove' in request.POST:
                    caption_id = request.POST.get('remove_caption')

                    if(ContentWritingTeam.delete_content_caption(caption_id)):
                        messages.success(request,'Caption deleted successfully!')
                    else:
                        messages.warning(request,'Something went wrong while deleting the caption')
                
                return redirect('content_writing_and_publications_team:edit_content_form_add_notes', content_id)

            context = {
                'user_data':user_data,
                'all_sc_ag':sc_ag,
                'content_id':content_id,
                'captions':captions,
                'has_content_access':has_content_access
            }

            return render(request,"Content/edit_content_form_add_notes.html",context)
        else:
            return render(request,"content_writing_and_publications_team/access_denied.html", {'all_sc_ag':sc_ag,'user_data':user_data})
    except Exception as e:
        logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
        ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
        return cv.custom_500(request)