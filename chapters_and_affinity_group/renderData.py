from django.contrib import messages
from .models import SC_AG_Members
from users.models import Members,Panel_Members
from port.models import Panels,Chapters_Society_and_Affinity_Groups,Teams,Roles_and_Position
from membership_development_team.models import Renewal_requests,Renewal_Sessions
import logging
from system_administration.system_error_handling import ErrorHandling
from system_administration.models import SC_AG_Data_Access
import traceback
from datetime import datetime
from central_events.models import Events
from django.http import JsonResponse, HttpResponse
import xlwt
from membership_development_team import renewal_data
from port.forms import Chapter_Society_Affinity_Groups_Form

class Sc_Ag:
    logger=logging.getLogger(__name__)
        
    def add_insb_members_to_sc_ag(request,sc_ag_primary,ieee_id_list,team_pk,position_id):
        '''This method adds an existing Member Registered in INSB to a SC or AG'''
        get_sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)
        count=0
        try:
            for ieee_id in ieee_id_list:
                if(SC_AG_Members.objects.filter(sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),member=Members.objects.get(ieee_id=ieee_id)).exists()):
                    messages.info(request,f"Member with IEEE ID: {ieee_id} already exists in Database")
                else:
                    new_sc_ag_member=SC_AG_Members.objects.create(sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)
                                                                ,member=Members.objects.get(ieee_id=ieee_id))
                    if team_pk is not None:
                        new_sc_ag_member.team=Teams.objects.get(pk=team_pk)
                    if position_id is not None:
                        new_sc_ag_member.position=Roles_and_Position.objects.get(id=position_id)
                    new_sc_ag_member.save()
                    count+=1
            messages.success(request,f"{count} new members were added to the Member List of {get_sc_ag.group_name} ")
            return True
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not add Member to Database. Something went wrong!")
            return False
    
    def make_panel_members_position_and_team_none_in_sc_ag_database(request,panel_id):
        '''This function finds the members in a panel and makes their Position and team None
        in the SC_AG_Members Table when required.'''
        try:
            get_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=panel_id))
            for member in get_panel_members:
                SC_AG_Members.objects.filter(member=Members.objects.get(ieee_id=member.member.ieee_id)).update(position=None,team=None)
            return True
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            return False
    
    def create_new_panel_of_sc_ag(request,sc_ag_primary,tenure_year,current_check,panel_start_time,panel_end_time):
        try:
            #Applying a logic where if the new panel is current, 
            # it will remove other current panels and place the SC AG Members position and team as None
            if(current_check):
                # Find the previous panel of SC AG which is current and make it False, and also make the position=None, Team=None in for the SC AG members that are in that panel
                previous_current_panel=Panels.objects.filter(panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),current=True)
                if(previous_current_panel.exists()):
                    # Update the Position,Team of SC AG members in that panel as None
                    for panel in previous_current_panel:
                        if(Sc_Ag.make_panel_members_position_and_team_none_in_sc_ag_database(request=request,panel_id=panel.pk)):
                            # set the current value of Panel to False
                            panel.current=False
                            panel.save()
                        else:
                            return False
            new_sc_ag_panel=Panels.objects.create(year=tenure_year,creation_time=panel_start_time,current=current_check,panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),panel_end_time=panel_end_time)
            new_sc_ag_panel.save()
            messages.success(request,f"A new panel with Tenure {new_sc_ag_panel.year} was created!")
            return True
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not create panel. Something went worng!")
            return False
    
    def update_sc_ag_panel(request,sc_ag_primary,panel_pk,panel_tenure,is_current_check,panel_start_date,panel_end_date):
        try:
            # get the panel
            panel_to_update=Panels.objects.get(pk=panel_pk)
            # first check if the user wants to make a non current panel to current
            if(is_current_check and (panel_to_update.current==False)):
                # find panels which are current now and make them false
                previous_current_panel=Panels.objects.filter(panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),current=True)
                if(previous_current_panel.exists()):
                    # Update the Position,Team of SC AG members in that panel as None
                    for panel in previous_current_panel:
                        if(Sc_Ag.make_panel_members_position_and_team_none_in_sc_ag_database(request=request,panel_id=panel.pk)):
                            # set the current value of Panel to False
                            panel.current=False
                            panel.save()
                        else:
                            return False
                # now get the members of the panel and update their team and Position in SC-AG members Table
                members_in_panel=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=panel_pk))
                for member in members_in_panel:
                    if member.team is None:
                        # update team as none
                        SC_AG_Members.objects.filter(member=Members.objects.get(ieee_id=member.member.ieee_id)).update(team=None,position=Roles_and_Position.objects.get(id=member.position.id))                
                    else:
                        SC_AG_Members.objects.filter(member=Members.objects.get(ieee_id=member.member.ieee_id)).update(team=Teams.objects.get(primary=member.team.primary),position=Roles_and_Position.objects.get(id=member.position.id))
                #now update the panel
                panel_to_update.current=True
                panel_to_update.year=panel_tenure
                panel_to_update.creation_time=panel_start_date
                panel_to_update.panel_end_time=panel_end_date
                panel_to_update.save()
                messages.success(request,"Panel Information was updated!")
                return True
            # then we check if we are making a current panel to a non current panel.
            elif(not is_current_check and panel_to_update.current):
                # Make positions and Teams of Members of that panel as None
                if(Sc_Ag.make_panel_members_position_and_team_none_in_sc_ag_database(request=request,panel_id=panel_to_update.pk)):
                    panel_to_update.current=False
                    panel_to_update.year=panel_tenure
                    panel_to_update.creation_time=panel_start_date
                    panel_to_update.panel_end_time=panel_end_date
                    panel_to_update.save()
                    messages.success(request,"Panel Information was updated!")
                    return True
                else:
                    return False
            else:
                # for all other instances update normally
                panel_to_update.current=is_current_check
                panel_to_update.year=panel_tenure
                panel_to_update.creation_time=panel_start_date
                panel_to_update.panel_end_time=panel_end_date
                panel_to_update.save()
                messages.success(request,"Panel Information was updated!")
                return True
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not Update Panel. Something went wrong!")
            return False

    def delete_sc_ag_panel(request,sc_ag_primary,panel_pk):
        try:
            # get the panel to delete
            get_panel=Panels.objects.get(id=panel_pk,panel_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary))
            # get the members of the panel to delete
            get_panel_members=Panel_Members.objects.filter(tenure=Panels.objects.get(id=panel_pk))
            for i in get_panel_members:
                if(get_panel.current):
                    #if panel is current, change position,Team in SC AG Members as well. Position=None, Team=None
                    SC_AG_Members.objects.filter(member=Members.objects.get(ieee_id=i),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).update(team=None,position=None)
                # delete members from panel
                i.delete()
            # delete panel
            get_panel.delete()
            messages.info(request,"A Panel was Deleted!")
            return True
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not Delete Panel. Something went wrong!")
            return False
            
        
    
    def add_sc_ag_members_to_panel(request,panel_id,memberList,position_id,team,sc_ag_primary):
        '''This method adds Members from SC_AG to their panels'''
        try:
            count=0
            for i in memberList:
                # check if the member already exists in the panel
                check_existing_member=Panel_Members.objects.filter(tenure=Panels.objects.get(id=panel_id),member=Members.objects.get(ieee_id=i))
                # get the Member from SC AG Database as well
                member_in_sc_ag=SC_AG_Members.objects.filter(sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),member=Members.objects.get(ieee_id=i))
                # get the panel details
                get_panel=Panels.objects.get(id=panel_id)
                if(check_existing_member.exists()):
                    # if exists, then update the members position with new Team and Positions
                    check_existing_member.update(position=Roles_and_Position.objects.get(id=position_id))
                    # Update members position and team in SC AG members database as well if the panel is current
                    if(get_panel.current):
                        member_in_sc_ag.update(position=Roles_and_Position.objects.get(id=position_id))
                    if team is None:
                        check_existing_member.update(team=None)
                        if(get_panel.current):
                            member_in_sc_ag.update(team=None)
                    else:
                        check_existing_member.update(team=Teams.objects.get(primary=team))
                        if(get_panel.current):
                            member_in_sc_ag.update(team=Teams.objects.get(primary=team))
                    messages.info(request,f"Member {i} already existed in the panel. Their Position and Team were updated!")
                else:
                    # Now create a new panel Member for the Panel and SC-AG
                    if(team is None):
                        # if team is not passed, it stays none
                        new_paneL_member=Panel_Members.objects.create(
                            tenure=Panels.objects.get(id=panel_id),
                            member=Members.objects.get(ieee_id=i),
                            position=Roles_and_Position.objects.get(id=position_id),
                            team=None
                        )
                        new_paneL_member.save()
                        if(get_panel.current):
                            member_in_sc_ag.update(position=Roles_and_Position.objects.get(id=position_id),team=None)
                        count+=1
                    else:
                        # create new panel Member with Team info if team info is given
                        new_paneL_member=Panel_Members.objects.create(
                            tenure=Panels.objects.get(id=panel_id),
                            member=Members.objects.get(ieee_id=i),
                            position=Roles_and_Position.objects.get(id=position_id),
                            team=Teams.objects.get(primary=team)
                        )
                        new_paneL_member.save()
                        if(get_panel.current):
                            member_in_sc_ag.update(position=Roles_and_Position.objects.get(id=position_id),team=Teams.objects.get(primary=team))
                        count+=1
            if(count>1):
                # if multiple members were added then show this message
                messages.success(request,f"{count} new members were added to the panel")              
            elif(count==1):
                # else show a singular message
                messages.success(request,f"{count} new member was added to the panel")              
            return True
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not add Member to panel. Something went wrong!")
            return False
    
    def remove_sc_ag_member_from_panel(request,panel_id,member_ieee_id,sc_ag_primary):
        """ This Method removes Members from SC_AG  Panels and also makes their Position and Team in SC Ag member table None"""
        try:
            member_in_panel=Panel_Members.objects.filter(tenure=Panels.objects.get(pk=panel_id),member=Members.objects.get(ieee_id=member_ieee_id))
            for i in member_in_panel:
                member_in_sc_ag=SC_AG_Members.objects.filter(sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary),member=Members.objects.get(ieee_id=member_ieee_id))
                member_in_sc_ag.update(team=None,position=None)
                i.delete()
            messages.error(request,f"{i.member.name} was removed from the panel!")
            return True
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not remove member from panel. Something went wrong!")
            return False
    
    def generate_renewal_excel_sheet(request,sc_ag_primary,renewal_session_id):
        '''This method generates excel sheet for the SC AG's about their Renewal Requests'''
        try:    
            date=datetime.now()
            # get renewal session
            session_name=renewal_data.get_renewal_session_name(pk=renewal_session_id)
            # get sc ag
            get_sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)
            date=datetime.now()
            response = HttpResponse(content_type='application/ms-excel')  # declaring content type for the excel files
            # setting filename
            response['Content-Disposition'] = f'attachment; filename=Renewal Application - ' +\
                get_sc_ag.group_name + '-' +\
                session_name + ' - ' +\
                str(date.strftime('%m/%d/%Y')) + \
                '.xls'  # making files downloadable with name of session and timestamp
            # adding encoding to the workbook
            workBook = xlwt.Workbook(encoding='utf-8')
            # opening an worksheet to work with the columns
            workSheet = workBook.add_sheet(f'Renewal Request List')
            
            # generating the first row
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            # Defining columns that will stay in the first row
            columns = ['Name','IEEE ID', 'Associated Email','IEEE Email','Contact No','Transaction ID','Member Comment',
                    'Renewal Status']
            # Defining first column
            for column in range(len(columns)):
                workSheet.write(row_num, column, columns[column], font_style)

            # reverting font style to default
            font_style = xlwt.XFStyle()
            
            # get values of renewal requests for sc ag as rows, checking manually
            if(int(sc_ag_primary)==2):
                rows=Renewal_requests.objects.filter(session_id=Renewal_Sessions.objects.get(pk=renewal_session_id),pes_renewal_check=True).values_list(
                    'name','ieee_id','email_associated','email_ieee','contact_no','transaction_id','comment','renewal_status')
            elif(int(sc_ag_primary)==3):
                rows=Renewal_requests.objects.filter(session_id=Renewal_Sessions.objects.get(pk=renewal_session_id),ras_renewal_check=True).values_list(
                    'name','ieee_id','email_associated','email_ieee','contact_no','transaction_id','comment','renewal_status')
            elif(int(sc_ag_primary)==4):
                rows=Renewal_requests.objects.filter(session_id=Renewal_Sessions.objects.get(pk=renewal_session_id),ias_renewal_check=True).values_list(
                    'name','ieee_id','email_associated','email_ieee','contact_no','transaction_id','comment','renewal_status')

            elif(int(sc_ag_primary)==5):
                            rows=Renewal_requests.objects.filter(session_id=Renewal_Sessions.objects.get(pk=renewal_session_id),wie_renewal_check=True).values_list(
                                'name','ieee_id','email_associated','email_ieee','contact_no','transaction_id','comment','renewal_status')

            # write in the rows one by one object
            for row in rows:
                row_num+=1 #increment rows at first as first row is written as heading
                for col_num in range(len(row)):
                    #write in the rows
                    workSheet.write(row_num, col_num, str(row[col_num]), font_style) 
            # save the workbook
            workBook.save(response)
            # return the workbook as response to download
            return response
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not generate Excel sheet! Something went wrong!")
            return False
    
    def get_data_access_members(request,sc_ag_primary):
        '''This function fetches all the members from data access table'''
        try:
            get_data_access_members=SC_AG_Data_Access.objects.filter(data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).order_by('-id')
            return get_data_access_members
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not fetch members for Data Access! Something went wrong!")
            return False
                
    def add_sc_ag_member_to_data_access(request,member_list,sc_ag_primary):
        '''This function adds member to data access table'''
        try:
            for i in member_list:
                # first check if the member already exists in the data access table for that SC AG
                if(SC_AG_Data_Access.objects.filter(member=SC_AG_Members.objects.get(member=Members.objects.get(ieee_id=i),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)),data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)).exists()):
                    messages.info(request,"The member already exists in the Database. Do Search for the member!")
                else:
                    new_member_in_table=SC_AG_Data_Access.objects.create(
                        member=SC_AG_Members.objects.get(member=Members.objects.get(ieee_id=i),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)),data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)
                    )
                    new_member_in_table.save()
                    messages.success(request,f"{new_member_in_table.member.member.ieee_id} added in the View Access Table.")
            return True
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not add Member! Something went wrong!")
            return False
    
    def update_sc_ag_member_access(*args, **kwargs):
        '''This function updates the access of the member in the data access table'''
        try:
            # get the query at first with member ieee id and sc_ag_primary
            get_query=SC_AG_Data_Access.objects.filter(member=SC_AG_Members.objects.get(member=Members.objects.get(ieee_id=kwargs['member']),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=kwargs['sc_ag_primary'])),data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=kwargs['sc_ag_primary']))
            if(get_query.exists()):
                # if query exists then only update
                get_query.update(
                    # get the values from kwargs. To avoid any error or misunderstanding the 'key's of the kwargs were kept same as the model(SC_AG_Data_Access) attributes name
                    member_details_access=kwargs['member_details_access'],
                    create_event_access=kwargs['create_event_access'],
                    event_details_edit_access=kwargs['event_details_edit_access'],
                    panel_edit_access=kwargs['panel_edit_access'],
                    membership_renewal_access=kwargs['membership_renewal_access'],
                    manage_access=kwargs['manage_access']
                )
                messages.success(kwargs['request'],f"Data Access for {kwargs['member']} was updated!")
                return True
            else:
                messages.error(kwargs['request'],"Can not Update Data Access for the Member!")
                return False
            
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(kwargs['request'],"Can not Data Access for the Member! Something went wrong!")
            return False
    
    def remove_member_from_data_access(request,member,sc_ag_primary):
        '''This function removes member from data access table'''
        try:
            get_query=SC_AG_Data_Access.objects.filter(member=SC_AG_Members.objects.get(member=Members.objects.get(ieee_id=member),sc_ag=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary)),data_access_of=Chapters_Society_and_Affinity_Groups.objects.get(primary=sc_ag_primary))
            if(get_query.exists()):
                messages.info(request,f"{get_query[0].member} was removed from the View Access!")
                get_query.delete()
                return True
            else:
                return False
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,"Can not remove member from Data Access! Something went wrong!")
            return False
        
    def main_website_info(request,primary,about_description,about_image,background_image,
                        mission_description,mission_image,vision_description,vision_picture,
                        what_is_this_description,why_join_it,what_activites_it_has,how_to_join):
        try:
            sc_ag = Chapters_Society_and_Affinity_Groups.objects.get(primary = primary)
            sc_ag.about_description =about_description
            sc_ag.sc_ag_logo = about_image
            sc_ag.background_image = background_image
            sc_ag.mission_description = mission_description
            sc_ag.mission_picture = mission_image
            sc_ag.vision_description = vision_description
            sc_ag.vision_picture = vision_picture
            sc_ag.what_is_this_description = what_is_this_description
            sc_ag.why_join_it = why_join_it
            sc_ag.what_activites_it_has = what_activites_it_has
            sc_ag.how_to_join = how_to_join

            sc_ag.save()

            return True
        except Exception as e:
            Sc_Ag.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
            ErrorHandling.saveSystemErrors(error_name=e,error_traceback=traceback.format_exc())
            messages.error(request,f"Could not update the main page of Sc_Ag group = {primary}!")
            return False
        
    def get_sc_ag(primary):

        return Chapters_Society_and_Affinity_Groups.objects.get(primary = primary)
    
    def get_form_data(primary):
        main_webpage_information = Sc_Ag.get_sc_ag(primary)
        form = Chapter_Society_Affinity_Groups_Form({'about_description':main_webpage_information.about_description,
                                                         'mission_description':main_webpage_information.mission_description,
                                                         'vision_description':main_webpage_information.vision_description,
                                                         'what_is_this_description':main_webpage_information.what_is_this_description,
                                                         'why_join_it':main_webpage_information.why_join_it,
                                                         'what_activites_it_has':main_webpage_information.what_activites_it_has,
                                                         'how_to_join':main_webpage_information.how_to_join})
        
        return form


    
    