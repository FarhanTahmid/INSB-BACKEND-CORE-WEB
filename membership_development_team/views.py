from django.shortcuts import render,redirect
from django.db import DatabaseError, IntegrityError, InternalError
from users.models import Members
from port.models import Teams
from system_administration.models import MDT_Data_Access
from recruitment import renderData
from django.db import connections
from django.contrib.auth.decorators import login_required
from . models import Renewal_Sessions,Renewal_requests
from recruitment.models import recruitment_session
from . import renewal_data
from . import renderData
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseServerError
import datetime
import xlwt
from django.contrib import messages
from django.urls import reverse
from port.models import Roles_and_Position,Teams
from django.conf import settings




# Create your views here.
def md_team_homepage(request):
    '''Loads the data for homepage of MDT TEAM'''
    
    
    #Loading data of the co-ordinators, co ordinator id is 9,
    co_ordinators=renderData.MDT_DATA.get_member_with_postion(9)
    #Loading data of the incharges, incharge id is 10
    in_charges=renderData.MDT_DATA.get_member_with_postion(10)
    #Loading data of the cor-volunteers, core-volunteer id is 11
    core_volunteers=renderData.MDT_DATA.get_member_with_postion(11)
    #Loading data of the cor-volunteers, volunteer id is 12
    volunteers=renderData.MDT_DATA.get_member_with_postion(12)
    
    context={
        'co_ordinators':co_ordinators,
        'incharges':in_charges,
        'core_volunteers':core_volunteers,
        'volunteers':volunteers,
        'media_url':settings.MEDIA_URL
    }    
    
    return render(request,'md_team_homepage.html',context=context)

@login_required
def insb_members_list(request):
    
    '''This function is responsible to display all the member data in the page'''
    members=Members.objects.order_by('position')
    totalNumber=Members.objects.all().count()
    has_view_permission=True
    context={'members':members,'totalNumber':totalNumber,'has_view_permission':has_view_permission}
    
    
    
          
    return render(request,'insb_member_list.html',context=context)

@login_required
def member_details(request,ieee_id):
    '''This function loads an editable member details view for particular IEEE ID'''
    
    member_data=renderData.MDT_DATA.get_member_data(ieee_id=ieee_id)
    
    dob = datetime.datetime.strptime(str(
        member_data.date_of_birth), "%Y-%m-%d").strftime("%Y-%m-%d")
    sessions=recruitment_session.objects.all()
    renewal_session=Renewal_Sessions.objects.all()
    context={
        'member_data':member_data,
        'dob':dob,
        'sessions':sessions,
        'renewal_session':renewal_session,
        'media_url':settings.MEDIA_URL
    }
    if request.method=="POST":
        if request.POST.get('save_edit'):
            nsu_id=request.POST['nsu_id']
            ieee_id=request.POST['ieee_id']
            name=request.POST['name']
            contact_no=request.POST['contact_no']
            date_of_birth=request.POST['date_of_birth']
            email_ieee=request.POST['email_ieee']
            email_personal=request.POST['email_personal']
            facebook_url=request.POST['facebook_url']
            
            home_address=request.POST['home_address']
            major=request.POST['major']
            
            #updating member Details
            try:
                Members.objects.filter(ieee_id=ieee_id).update(nsu_id=nsu_id,
                                                               name=name,
                                                               contact_no=contact_no,
                                                               date_of_birth=date_of_birth,
                                                               email_ieee=email_ieee,
                                                               email_personal=email_personal,
                                                               facebook_url=facebook_url,
                                                               
                                                               home_address=home_address,
                                                               major=major)
                
                messages.info(request,"Member Info Was Updated. If you want to update the Members IEEE ID please contact the System Administrators")
                return redirect('membership_development_team:member_details',ieee_id)
            except Members.DoesNotExist:
                messages.info(request,"Sorry! Something went wrong! Try Again.")            
            
        if request.POST.get('delete_member'):
            #Deleting a member from database
            member_to_delete=Members.objects.get(ieee_id=ieee_id)
            member_to_delete.delete()
            return redirect('membership_development_team:members_list')
              
            
    
    return render(request,'member_details.html',context=context)

@login_required
def membership_renewal(request):
    '''This view loads the renewal homepage'''
    '''This function is responsible for the data handling for renewal Process and loads all the sessions'''
    #Load all sessions at first
    sessions=Renewal_Sessions.objects.order_by('-id')
    context={
        'sessions':sessions
    }
    if request.method=="POST":
        #MUST PERFORM TRY CATCH
        #Creating and inserting the data of the session
        try:
            session_name=request.POST['renewal_session']
            try:
                if(Renewal_Sessions.objects.get(session_name=session_name)):
                    messages.info(request,"A same session with this name already exists!")
            except Renewal_Sessions.DoesNotExist:
                session_time=datetime.datetime.now()
                add_session=Renewal_Sessions(session_name=session_name,session_time=session_time)
                add_session.save()
                return render(request,'renewal.html',context)
        except DatabaseError:
            messages.info(request,"Error Creating a new Session!")
            return DatabaseError
        
    return render(request,'renewal.html',context)

# no login required as this will open up for other people
def membership_renewal_form(request,pk):
    session_name=renewal_data.get_renewal_session_name(pk)
    context={
        'session_name':session_name,
        
    }
    
    if request.method=="POST":
        
        if(request.POST.get('apply')):
           
            name=request.POST['name']
            contact_no=request.POST['contact_no']
            email_personal=request.POST['email_personal']
            password=request.POST['password']
            confirm_password=request.POST['confirm_password']
            
            #check if check marks are checked in the form
            ieee_renewal=False
            pes_renewal=False
            ras_renewal=False
            ias_renewal=False
            wie_renewal=False
            if(request.POST.get('ieee')):
                ieee_renewal=True
            if(request.POST.get('pes')):
                pes_renewal=True
            if(request.POST.get('ras')):
                ras_renewal=True
            if(request.POST.get('ias')):
                ias_renewal=True
            if(request.POST.get('wie')):
                wie_renewal=True
            transaction_id=request.POST['trx_id']
            comment=request.POST['comment']
            if(password==confirm_password):
                
                
                #change here if ieee_id is allowed in the field
                #get_ieee_id=Members.objects.filter(email_personal=email_personal).values_list('ieee_id')
                
                try:
                    #encrypted_pass=renewal_data.encrypt_password(password=password)
                    renewal_instance=Renewal_requests(session_id=Renewal_Sessions.objects.get(id=pk,session_name=session_name),name=name,contact_no=contact_no,email_personal=email_personal,ieee_account_password=password,ieee_renewal_check=ieee_renewal,pes_renewal_check=pes_renewal,ras_renewal_check=ras_renewal,ias_renewal_check=ias_renewal,wie_renewal_check=wie_renewal,transaction_id=transaction_id,comment=comment,renewal_status=False,view_status=False)
                    renewal_instance.save()
                    messages.info(request,"Application Successful!")
                except:
                    return HttpResponseServerError
            else:
                messages.info(request,"Two Passwords did not match!")   
        else:
            return HttpResponseBadRequest
    
    
    return render(request,'renewal_form.html',context)


@login_required
def renewal_session_data(request,pk):
    '''This view function loads all data for the renewal session including the members registered'''
    renewal_data.get_renewal_session_name(pk)
    session_name=renewal_data.get_renewal_session_name(pk)
    session_id=renewal_data.get_renewal_session_id(session_name=session_name)
    get_renewal_requests=Renewal_requests.objects.filter(session_id=session_id).values('id','name','email_personal','contact_no',).order_by('-id')
    #loading all the unviewed request count
    notification_count=Renewal_requests.objects.filter(session_id=session_id,view_status=False).count()
    #counting the renewed requests
    renewed_count=Renewal_requests.objects.filter(session_id=session_id,renewal_status=True).count()
    #counting the pending requests
    pending_count=Renewal_requests.objects.filter(session_id=session_id,renewal_status=False).count()
    #form link for particular sessions
    form_link="http:insbapp.pythonanywhere.com/membership_development_team/renewal_form/"+str(session_id)
    context={
        'session_name':session_name,
        'session_id':session_id,
        'requests':get_renewal_requests,
        'form_link':form_link,
        'notification_count':notification_count,
        'renewed_count':renewed_count,
        'pending_count':pending_count,
    }
    
    return render(request,'renewal_sessions.html',context)

@login_required
def renewal_request_details(request,pk,request_id):
    
    '''This function loads the datas for particular renewal requests'''
    
    renewal_request_details=Renewal_requests.objects.filter(id=request_id).values('name','email_personal','ieee_account_password','ieee_renewal_check','pes_renewal_check','ras_renewal_check','ias_renewal_check','wie_renewal_check','transaction_id','renewal_status','contact_no','comment','official_comment')
    name=renewal_request_details[0]['name']
    renewal_email=""
    has_comment=False
    for i in range(len(renewal_request_details)):
        renewal_email=renewal_request_details[i]['email_personal']
        if(renewal_request_details[i]['official_comment'] is not None):
            has_comment=True
    #changing the viewing status
    Renewal_requests.objects.filter(id=request_id).update(view_status=True)
    
    context={
        'id':request_id,
        'details':renewal_request_details,
        'has_comment':has_comment,
        'pk':pk,
        'name':name,
    }
    if request.method=="POST":
        if (request.POST.get('go_back')):
            return redirect('membership_development_team:renewal_session_data',pk)
        if(request.POST.get('renew_button')):
            try:
                #First check if the member is registered in the database or not, search with ASSOCIATED EMAIL (email_personal) and get ieee id with it
                member=Members.objects.get(email_personal=renewal_email)
                ieee_id=member.ieee_id #getting the ieee id
                    
                #update data in main registered Members database
                Members.objects.filter(ieee_id=ieee_id).update(last_renewal=pk)
                
                # #Update in renewal requests database.
                Renewal_requests.objects.filter(id=request_id).update(renewal_status=True)
                
                # #show success message
                messages.info(request,f"Membership with IEEE ID {ieee_id} has been renewed!")
                return redirect('membership_development_team:request_details',pk,request_id)
            
            #Now if the member is not registered in the database
            except Members.DoesNotExist:
                
                # just Update the renewal request table and notify team that member is not registered in the main database
                Renewal_requests.objects.filter(id=request_id,session_id=pk).update(renewal_status=True)
                
                #show message
                messages.info(request,f"Membership has been renewed!\nThis member with the associated E-mail: {renewal_email} was not found in the INSB Registered Member Database!\nHowever, the system kept the Data of renewal!")
                
        
        #TO DELETE AN APPLICATION
        if(request.POST.get('delete_button')): 
            
            #getting member
            try:
                #getting member and deleting
                Renewal_requests.objects.get(id=request_id,session_id=pk).delete()
                return redirect('membership_development_team:renewal_session_data',pk)
            except Renewal_requests.DoesNotExist:
                messages.info(request,"Member could not be found!")
            except:
                messages.info(request,"Something went Wrong!")
            
        #TO UPDATE AN APPLICATIONS COMMENT BY MD TEAM
        if(request.POST.get('update_comment')):
            updated_comment=request.POST['official_comment']
            
            try:
                
                #Updating new comment with previous comment
                Renewal_requests.objects.filter(id=request_id,session_id=pk).update(official_comment=updated_comment)
                messages.info(request,"Comment Updated!")
                return redirect('membership_development_team:request_details',pk,request_id)
            except Renewal_requests.DoesNotExist:
                messages.info(request,"Something Went Wrong! Please refresh the page and try again")
                return redirect('membership_development_team:request_details',pk,request_id)
            
    return render(request,"renewal_request_details.html",context=context)

@login_required
def generateExcelSheet_renewal_requestList(request,session_id):
    
    '''This method generates excel sheets only for renewal recruitment details for particular sessions'''
    session_name=renewal_data.get_renewal_session_name(pk=session_id)
    date=datetime.datetime.now()
    response = HttpResponse(
        content_type='application/ms-excel')  # eclaring content type for the excel files
    response['Content-Disposition'] = f'attachment; filename=Renewal Application - ' +\
        session_name + ' - ' +\
        str(date.strftime('%m/%d/%Y')) + \
        '.xls'  # making files downloadable with name of session and timestamp
    # adding encoding to the workbook
    workBook = xlwt.Workbook(encoding='utf-8')
    # opening an worksheet to work with the columns
    workSheet = workBook.add_sheet(f'Application List')

    # generating the first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # Defining columns that will stay in the first row
    columns = ['Name', 'Associated Email','Contact No', 'IEEE Account Password', 'IEEE-Renewal', 'PES-Renewal', 'RAS-Renewal','IAS-Renewal','WIE-Renewal','Transaction ID','Any Comments?',
               'Renewal Status','MDT Comment']

    # Defining first column
    for column in range(len(columns)):
        workSheet.write(row_num, column, columns[column], font_style)

    # reverting font style to default
    font_style = xlwt.XFStyle()

    # getting all the values of members as rows with same session
    rows = Renewal_requests.objects.all().values_list('name',
                                             'email_personal',
                                             'contact_no',
                                             'ieee_account_password',
                                             'ieee_renewal_check','pes_renewal_check','ras_renewal_check','ias_renewal_check','wie_renewal_check',
                                             'transaction_id',
                                             'comment',
                                             'renewal_status',
                                             'official_comment')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            workSheet.write(row_num, col_num, str(row[col_num]), font_style)
    workBook.save(response)
    return (response)
    
    
    
@login_required
def generateExcelSheet_membersList(request):
    '''This method generates the excel files for The Registered INSB members for MDT'''
    date=datetime.datetime.now()
    response = HttpResponse(
        content_type='application/ms-excel')  # eclaring content type for the excel files
    response['Content-Disposition'] = f'attachment; filename=Registered Member List - ' +\
        str(date.strftime('%m/%d/%Y')) + \
        '.xls'  # making files downloadable with name of session and timestamp
    # adding encoding to the workbook
    workBook = xlwt.Workbook(encoding='utf-8')
    # opening an worksheet to work with the columns
    workSheet = workBook.add_sheet(f'Member-List')

    # generating the first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # Defining columns that will stay in the first row
    columns = ['IEEE ID','NSU ID', 'Name', 'Email (IEEE)','Email (Personal)', 'Major', 'Contact No', 'Home Address', 'Date Of Birth', 'Gender',
               'Facebook URL']

    # Defining first column
    for column in range(len(columns)):
        workSheet.write(row_num, column, columns[column], font_style)

    # reverting font style to default
    font_style = xlwt.XFStyle()

    # getting all the values of members as rows with same session
    rows = Members.objects.all().values_list('ieee_id',
                                             'nsu_id',
                                             'name',
                                             'email_ieee',
                                             'email_personal',
                                             'major',
                                             'contact_no',
                                             'home_address',
                                             'date_of_birth',
                                             'gender',
                                             'facebook_url')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            workSheet.write(row_num, col_num, str(row[col_num]), font_style)
    workBook.save(response)
    return (response)


@login_required
def data_access(request):
    
    # '''This function mantains all the data access works'''
    
    data_access=renderData.MDT_DATA.load_mdt_data_access()
    team_members=renderData.MDT_DATA.load_team_members()
    
    if request.method=="POST":
        if request.POST.get('access_update'):
            
            insb_member_details_permission=False
            recruitment_session_permission=False
            recruited_member_details_permission=False
            renewal_data_access_permission=False
            
            #GEtting values from checkbox
            if(request.POST.get('insb_member_details')):
                insb_member_details_permission=True
            if(request.POST.get('recruitment_session')):
                recruitment_session_permission=True
            if(request.POST.get('recruited_member_details')):
                recruited_member_details_permission=True
            if(request.POST.get('renewal_data_access')):
                renewal_data_access_permission=True
            ieee_id=request.POST['access_ieee_id']
            
            if(renderData.MDT_DATA.mdt_access_modifications(
                ieee_id=ieee_id,insb_member_details_permission=insb_member_details_permission,recruitment_session_permission=recruitment_session_permission,
                recruited_member_details_permission=recruited_member_details_permission,renewal_data_access_permission=renewal_data_access_permission
            )):
                messages.info(request,f"Permission Details Was updated For the Member with {ieee_id}")
            
            else:
                messages.info(request,f"Something Went Wrong! Please Contact System Administrator about this issue")
        if request.POST.get('remove_member'):
            try:
                Members.objects.filter(ieee_id=request.POST['remove_ieee_id']).update(team=None,position=Roles_and_Position.objects.get(id=13))   
                return redirect('membership_development_team:data_access')
            except:
                pass
            
           

    context={
        'data_access':data_access,
        'members':team_members,
        
    }
    return render(request,'data_access_table.html',context=context)