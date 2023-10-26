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
from django.http import JsonResponse, HttpResponse,HttpResponseBadRequest,HttpResponseServerError
import datetime
import xlwt
from django.contrib import messages
from django.urls import reverse
from port.models import Roles_and_Position,Teams
from django.conf import settings
from system_administration.render_access import Access_Render
from django.core.mail import send_mail
from . import email_sending
from central_branch.renderData import Branch
from users.renderData import LoggedinUser


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
    current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
    user_data=current_user.getUserData() #getting user data as dictionary file
    
    context={
        'co_ordinators':co_ordinators,
        'incharges':in_charges,
        'core_volunteers':core_volunteers,
        'volunteers':volunteers,
        'media_url':settings.MEDIA_URL,
        'user_data':user_data,
    }
    return render(request,'md_team_homepage.html',context=context)

@login_required
def insb_members_list(request):
    
    '''This function is responsible to display all the member data in the page'''
    if request.method=="POST":
        if request.POST.get("site_register"):
            
            return redirect('membership_development_team:site_registration')
        
    members=Members.objects.order_by('position')
    totalNumber=Members.objects.all().count()
    has_view_permission=True
    current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
    user_data=current_user.getUserData() #getting user data as dictionary file
    context={'members':members,'totalNumber':totalNumber,'has_view_permission':has_view_permission,'user_data':user_data}
    
    return render(request,'INSB Members/members_list.html',context=context)

@login_required
def member_details(request,ieee_id):
    '''This function loads an editable member details view for particular IEEE ID'''
    
    '''This has some views restrictions'''
    #Loading Access Permission
    user=request.user
    
    has_access=(renderData.MDT_DATA.insb_member_details_view_control(user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username))
    
    member_data=renderData.MDT_DATA.get_member_data(ieee_id=ieee_id)
    dob = datetime.strptime(str(
        member_data.date_of_birth), "%Y-%m-%d").strftime("%Y-%m-%d")
    sessions=recruitment_session.objects.all().order_by('-id')
    #getting the ieee account active status of the member
    active_status=renderData.MDT_DATA.get_member_account_status(ieee_id=ieee_id)
        
    renewal_session=Renewal_Sessions.objects.all().order_by('-id')
    current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
    user_data=current_user.getUserData() #getting user data as dictionary file
    context={
        
        'member_data':member_data,
        'dob':dob,
        'sessions':sessions,
        'renewal_session':renewal_session,
        'media_url':settings.MEDIA_URL,
        'active_status':active_status,
        'user_data':user_data,
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
            email_nsu=request.POST['email_nsu']
            facebook_url=request.POST['facebook_url']
            home_address=request.POST['home_address']
            major=request.POST['major_label']
            recruitment_session_value=request.POST['recruitment']
            renewal_session_value=request.POST['renewal']
            
            #checking if the recruitment and renewal session exists
            try:
                recruitment_session.objects.get(id=recruitment_session_value)
                 
            except:
                recruitment_session_value=None          
            try:
                Renewal_Sessions.objects.get(id=renewal_session_value)
                
            except:
                renewal_session_value=None 
            
            #updating member Details
            if (recruitment_session_value==None and renewal_session_value==None):
                try:
                    Members.objects.filter(ieee_id=ieee_id).update(nsu_id=nsu_id,
                                                               name=name,
                                                               contact_no=contact_no,
                                                               date_of_birth=date_of_birth,
                                                               email_ieee=email_ieee,
                                                               email_personal=email_personal,
                                                               email_nsu=email_nsu,
                                                               facebook_url=facebook_url,
                                                               home_address=home_address,
                                                               major=major,
                                                               session=None,
                                                               last_renewal_session=None 
                                                               )
                
                    messages.info(request,"Member Info Was Updated. If you want to update the Members IEEE ID please contact the System Administrators")
                    return redirect('membership_development_team:member_details',ieee_id)
                except Members.DoesNotExist:
                    messages.info(request,"Sorry! Something went wrong! Try Again.")
            elif renewal_session_value==None:
                try:
                    Members.objects.filter(ieee_id=ieee_id).update(nsu_id=nsu_id,
                                                               name=name,
                                                               contact_no=contact_no,
                                                               date_of_birth=date_of_birth,
                                                               email_ieee=email_ieee,
                                                               email_personal=email_personal,
                                                               email_nsu=email_nsu,
                                                               facebook_url=facebook_url,
                                                               home_address=home_address,
                                                               major=major,
                                                               session=recruitment_session.objects.get(id=recruitment_session_value),
                                                               last_renewal_session=None 
                                                               )
                
                    messages.info(request,"Member Info Was Updated. If you want to update the Members IEEE ID please contact the System Administrators")
                    return redirect('membership_development_team:member_details',ieee_id)
                except Members.DoesNotExist:
                    messages.info(request,"Sorry! Something went wrong! Try Again.")
            
            elif(recruitment_session_value==None):
                try:
                    Members.objects.filter(ieee_id=ieee_id).update(nsu_id=nsu_id,
                                                               name=name,
                                                               contact_no=contact_no,
                                                               date_of_birth=date_of_birth,
                                                               email_ieee=email_ieee,
                                                               email_personal=email_personal,
                                                               email_nsu=email_nsu,
                                                               facebook_url=facebook_url,
                                                               home_address=home_address,
                                                               major=major,
                                                               session=None,
                                                               last_renewal_session=Renewal_Sessions.objects.get(id=renewal_session_value) 
                                                               )
                
                    messages.info(request,"Member Info Was Updated. If you want to update the Members IEEE ID please contact the System Administrators")
                    return redirect('membership_development_team:member_details',ieee_id)
                except Members.DoesNotExist:
                    messages.info(request,"Sorry! Something went wrong! Try Again.")
            else:
                try:
                    Members.objects.filter(ieee_id=ieee_id).update(nsu_id=nsu_id,
                                                               name=name,
                                                               contact_no=contact_no,
                                                               date_of_birth=date_of_birth,
                                                               email_ieee=email_ieee,
                                                               email_personal=email_personal,
                                                               email_nsu=email_nsu,
                                                               facebook_url=facebook_url,
                                                               home_address=home_address,
                                                               major=major,
                                                               session=recruitment_session.objects.get(id=recruitment_session_value),
                                                               last_renewal_session=Renewal_Sessions.objects.get(id=renewal_session_value) 
                                                               )
                
                    messages.info(request,"Member Info Was Updated. If you want to update the Members IEEE ID please contact the System Administrators")
                    return redirect('membership_development_team:member_details',ieee_id)
                except Members.DoesNotExist:
                    messages.info(request,"Sorry! Something went wrong! Try Again.")
                        
        if request.POST.get('delete_member'):
            #Deleting a member from database
            member_to_delete=Members.objects.get(ieee_id=ieee_id)
            member_to_delete.delete()
            return redirect('membership_development_team:members_list')
              
            
    if(has_access):
        return render(request,'INSB Members/member_details.html',context=context)
    else:
        return render(request,'access_denied.html',context)
    
@login_required
def membership_renewal(request):
    '''This view loads the renewal homepage'''
    '''This function is responsible for the data handling for renewal Process and loads all the sessions'''
    #Load all sessions at first
    sessions=Renewal_Sessions.objects.order_by('-id')

    current_user=LoggedinUser(request.user) #Creating an Object of logged in user with current users credentials
    user_data=current_user.getUserData() #getting user data as dictionary file


    context={
        'sessions':sessions,
        'user_data':user_data,
    }
    if request.method=="POST":
        #MUST PERFORM TRY CATCH
        #Creating and inserting the data of the session
        try:
            session_name=request.POST['renewal_session']
            try:
                if(Renewal_Sessions.objects.get(session_name=session_name)):
                    messages.error(request,"A same session with this name already exists!")
                    return redirect('membership_development_team:membership_renewal')
            except Renewal_Sessions.DoesNotExist:
                session_time=datetime.datetime.now()
                add_session=Renewal_Sessions(session_name=session_name,session_time=session_time)
                add_session.save()
                messages.success(request,"A new session has been created!")
                return redirect('membership_development_team:membership_renewal')
        except DatabaseError:
            messages.info(request,"Error Creating a new Session!")
            return redirect('membership_development_team:membership_renewal')
        
    return render(request,'Renewal/renewal_homepage.html',context)

# no login required as this will open up for other people
from system_administration.render_access import Access_Render
from datetime import datetime
def membership_renewal_form(request,pk):
    
    #rendering access to view the message section
    has_access_to_view=False
    if (request.user.is_authenticated):
        if((Access_Render.faculty_advisor_access(request.user.username)) or (Access_Render.eb_access(request.user.username)) or (Access_Render.team_co_ordinator_access(team_id=renderData.MDT_DATA.get_team_id(),username=request.user.username)) or (Access_Render.system_administrator_superuser_access(request.user.username)) or (Access_Render.system_administrator_staffuser_access(request.user.username))):
            has_access_to_view=True
            
        
    session_name=renewal_data.get_renewal_session_name(pk)
    
    #load renewal form credentials
    form_credentials=renderData.MDT_DATA.load_form_data_for_particular_renewal_session(renewal_session_id=pk)
    #performing try catch because the form might not contain credential data
    try:
        form_credentials_further_contact_info=Members.objects.get(ieee_id=form_credentials.further_contact_member_id)
    except:
        form_credentials_further_contact_info="none"
    
    if(form_credentials==False):
        messages.info(request,"No Form Data was Updated. Please Update form data from the Renewal Session page, Edit Renewal Form Credentials")
    
    
    context={
        'session_name':session_name,
        'form_credentials':form_credentials,
        'further_contact':form_credentials_further_contact_info,
        'has_access_to_view':has_access_to_view,
    }
    
    if request.method=="POST":
        
        if(request.POST.get('apply')):
           
            ieee_id=request.POST['ieee_id']
            name=request.POST['name']
            contact_no=request.POST['contact_no']
            email_associated=request.POST['email_associated']
            email_ieee=request.POST['email_ieee']
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
                    renewal_instance=Renewal_requests(timestamp=datetime.now(),session_id=Renewal_Sessions.objects.get(id=pk,session_name=session_name),ieee_id=ieee_id,name=name,contact_no=contact_no,email_associated=email_associated,email_ieee=email_ieee,ieee_account_password=password,ieee_renewal_check=ieee_renewal,pes_renewal_check=pes_renewal,ras_renewal_check=ras_renewal,ias_renewal_check=ias_renewal,wie_renewal_check=wie_renewal,transaction_id=transaction_id,comment=comment,renewal_status=False,view_status=False)
                    renewal_instance.save()
                    
                    # Send mail upon form submission to users IEEE Account Associated mail
                    renewal_check_dict={
                        'IEEE Membership':ieee_renewal,
                        'IEEE PES Membership':pes_renewal,
                        'IEEE RAS Membership': ras_renewal,
                        'IEEE IAS Membership':ias_renewal,
                        'IEEE WIE Membership':wie_renewal,
                    }
                    email_sending.send_emails_upon_filling_up_renewal_form(reciever_name=name,reciever_email=email_associated,renewal_session=session_name,renewal_check_dict=renewal_check_dict)
                    return redirect('membership_development_team:renewal_form_success',pk)
                except:
                    return HttpResponseServerError
            else:
                messages.info(request,"Two Passwords did not match!")   
        else:
            return HttpResponseBadRequest
    
    
    return render(request,'Renewal/renewal_form.html',context)

def membership_renewal_form_success(request,pk):
    context={
        'pk':pk
    }
    return render(request,"Renewal/renewal_form_confirmation.html",context)


@login_required
def getRenewalStats(request):
    if request.method=="GET":
        session_id=request.GET.get('session_id')
        #loading all the unviewed request count
        notification_count=Renewal_requests.objects.filter(session_id=session_id,view_status=False).count()
        #counting the renewed requests
        renewed_count=Renewal_requests.objects.filter(session_id=session_id,renewal_status=True).count()
        #counting the pending requests
        pending_count=Renewal_requests.objects.filter(session_id=session_id,renewal_status=False).count()
        context={
            "labels":["Applications Not Yet Viewed","Total Pending Applications","Total Renewed Applications"],
            "values":[notification_count,pending_count,renewed_count]
        }
    return JsonResponse(context)    

    


@login_required
def renewal_session_data(request,pk):
    '''This view function loads all data for the renewal session including the members registered'''
    session_name=renewal_data.get_renewal_session_name(pk)
    session_id=renewal_data.get_renewal_session_id(session_name=session_name)
    get_renewal_requests=Renewal_requests.objects.filter(session_id=session_id).values('id','name','email_associated','email_ieee','contact_no','ieee_id').order_by('id')
        
    #loading team member data for form credential edit
    load_team_members=renderData.MDT_DATA.load_team_members()
    
    #form link for particular sessions
    form_link=f"{request.META['HTTP_HOST']}/portal/membership_development_team/renewal_form/"+str(session_id)
    
    #try loading form data to notify user if form credentials has been updated or not for that session with button glow in "Update Form Credentials"
    has_form_data=False
    form_data=None
    if(renderData.MDT_DATA.load_form_data_for_particular_renewal_session(renewal_session_id=pk)==False):
        has_form_data=False
    else:
        form_data=renderData.MDT_DATA.load_form_data_for_particular_renewal_session(renewal_session_id=pk)
        has_form_data=True
    
    if request.method=="POST":
        if request.POST.get('update_form_credentials'):
            
            form_description=request.POST['form_description']
            ieee_membership_amount=request.POST['ieee_membership_amount']
            ieee_ras_membership_amount=request.POST['ieee_ras_membership_amount']
            ieee_pes_membership_amount=request.POST['ieee_pes_membership_amount']
            ieee_ias_membership_amount=request.POST['ieee_ias_membership_amount']
            ieee_wie_membership_amount=request.POST['ieee_wie_membership_amount']
            bkash_payment_number=request.POST['bkash_payment_number']
            nagad_payment_number=request.POST['nagad_payment_number']
            further_contact_member_id=request.POST['further_contact_member_id']
            
            #update form credentials
            renderData.MDT_DATA.create_form_data_for_particular_renewal_session(
                renewal_session_id=pk,
                form_description=form_description,
                ieee_membership_amount=ieee_membership_amount,
                ieee_ias_membership_amount=ieee_ias_membership_amount,
                ieee_pes_membership_amount=ieee_pes_membership_amount,
                ieee_ras_membership_amount=ieee_ras_membership_amount,
                ieee_wie_membership_amount=ieee_wie_membership_amount,
                bkash_payment_number=bkash_payment_number,
                nagad_payment_number=nagad_payment_number,
                further_contact_member_id=further_contact_member_id
            )
            return redirect('membership_development_team:renewal_session_data',pk) 
    context={
        'session_name':session_name,
        'form_data':form_data,
        'session_id':session_id,
        'requests':get_renewal_requests,
        'form_link':form_link,
        'mdt_team_member':load_team_members,
        'has_form_data':has_form_data,
    }
    
    return render(request,'Renewal/renewal_session_details.html',context)

from .models import Renewal_Form_Info
@login_required
def renewal_request_details(request,pk,request_id):
    '''This function loads the datas for particular renewal requests'''
    #check if the user has access to view
    user=request.user
    has_access=(renderData.MDT_DATA.renewal_data_access_view_control(user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username))
    
    renewal_request_details=Renewal_requests.objects.filter(id=request_id).values('timestamp','name','ieee_id','email_associated','ieee_account_password','ieee_renewal_check','pes_renewal_check','ras_renewal_check','ias_renewal_check','wie_renewal_check','transaction_id','renewal_status','contact_no','comment','official_comment')
    name=renewal_request_details[0]['name']
    
    has_comment=False
    for i in range(len(renewal_request_details)):
        ieee_id=renewal_request_details[i]['ieee_id']
        if(renewal_request_details[i]['official_comment'] is not None):
            has_comment=True
    #changing the viewing status
    Renewal_requests.objects.filter(id=request_id).update(view_status=True)
    
    # INVOICE
    # get form amount of money
    try:
        renewal_amount_dict={
            'IEEE Membership':renderData.MDT_DATA.getPaymentAmount(request_id=request_id,info='ieee',form_id=pk),
            'IEEE PES Membership':renderData.MDT_DATA.getPaymentAmount(request_id=request_id,info='pes',form_id=pk),
            'IEEE RAS Membership':renderData.MDT_DATA.getPaymentAmount(request_id=request_id,info='ras',form_id=pk),
            'IEEE IAS Membership':renderData.MDT_DATA.getPaymentAmount(request_id=request_id,info='ias',form_id=pk),
            'IEEE WIE Membership':renderData.MDT_DATA.getPaymentAmount(request_id=request_id,info='wie',form_id=pk),
        }
    except:
        messages.error(request,"Please Edit Form Credentials to view.")
        return redirect('membership_development_team:renewal_session_data',pk)

    
    try:
        total_amount=(
            renewal_amount_dict['IEEE Membership']+
            renewal_amount_dict['IEEE PES Membership']+
            renewal_amount_dict['IEEE RAS Membership']+
            renewal_amount_dict['IEEE IAS Membership']+
            renewal_amount_dict['IEEE WIE Membership']
        )
        
    except:
        total_amount=0
        
    current_request=Renewal_requests.objects.get(id=request_id)
    next_request=Renewal_requests.objects.filter(pk__gt=current_request.pk,session_id=pk).first()
    
    if next_request:
        next_request_id=next_request.pk
        has_next_request=True
    else:
        next_request_id=None
        has_next_request=False
    
    print(next_request_id)
    print(has_next_request)
    
        
    context={
        'id':request_id,
        'details':renewal_request_details,
        'has_comment':has_comment,
        'has_next_request':has_next_request,
        'next_request_id':next_request_id,
        'pk':pk,
        'name':name,
        'renewal_amount':renewal_amount_dict,
        'total_amount':total_amount,
    }
    
    
    if request.method=="POST":
        if (request.POST.get('go_back')):
            return redirect('membership_development_team:renewal_session_data',pk)
        if(request.POST.get('renew_button')):
            
            try:
                    
                #update data in main registered Members database
                get_renewal_session=Renewal_Sessions.objects.get(id=pk)
                # Update and Check if the member is registered in the database or not.
                member=Members.objects.get(ieee_id=ieee_id)
                member.last_renewal_session=Renewal_Sessions.objects.get(id=get_renewal_session.id)
                member.save()
                                
                # #Update in renewal requests database.
                Renewal_requests.objects.filter(id=request_id).update(renewal_status=True)
                
                # #show success message
                messages.success(request,f"Membership with IEEE ID {ieee_id} has been renewed!")
                return redirect('membership_development_team:request_details',pk,request_id)
            
            #Now if the member is not registered in the database
            except Members.DoesNotExist:
                
                # just Update the renewal request table and notify team that member is not registered in the main database
                Renewal_requests.objects.filter(id=request_id,session_id=pk).update(renewal_status=True)
                
                #show message
                messages.success(request,f"Membership has been renewed!\nThis member with the associated IEEE ID: {ieee_id} was not found in the INSB Registered Member Database!\nHowever, the system kept the Data of renewal!")
        
        #TO DELETE AN APPLICATION
        if(request.POST.get('delete_button')): 
            
            #getting member
            try:
                #getting member and deleting
                Renewal_requests.objects.get(id=request_id,session_id=pk).delete()
                messages.error(request,"Renewal Application was Deleted")
                return redirect('membership_development_team:renewal_session_data',pk)
            except Renewal_requests.DoesNotExist:
                messages.error(request,"Renewal Application could not be found!")
                return redirect('membership_development_team:renewal_session_data',pk)

            except:
                messages.error(request,"Something went Wrong!")
                return redirect('membership_development_team:renewal_session_data',pk)

            
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
    if(has_access):        
        return render(request,"Renewal/renewal_application_details.html",context=context)
    else:
        return render(request,'access_denied.html')
    
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
    columns = ['Name','IEEE ID', 'Associated Email','IEEE Email','Contact No', 'IEEE Account Password', 'IEEE-Renewal', 'PES-Renewal', 'RAS-Renewal','IAS-Renewal','WIE-Renewal','Transaction ID','Any Comments?',
               'Renewal Status','MDT Comment']

    # Defining first column
    for column in range(len(columns)):
        workSheet.write(row_num, column, columns[column], font_style)

    # reverting font style to default
    font_style = xlwt.XFStyle()

    # getting all the values of members as rows with same session
    rows = Renewal_requests.objects.all().values_list('name',
                                            'ieee_id',
                                             'email_associated',
                                             'email_ieee',
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

    # getting all the values of members as rows ORDERED BY POSITION
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
                                             'facebook_url').order_by('position')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            workSheet.write(row_num, col_num, str(row[col_num]), font_style)
    workBook.save(response)
    return (response)


@login_required
def data_access(request):
    
    # '''This function mantains all the data access works'''
    #Only sub eb of that team can access the page
    user=request.user
    has_access=(Access_Render.team_co_ordinator_access(team_id=renderData.MDT_DATA.get_team_id(),username=user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username) or Access_Render.eb_access(user.username))
    
    data_access=renderData.MDT_DATA.load_mdt_data_access()
    team_members=renderData.MDT_DATA.load_team_members()
    #load all position for insb members
    position=Branch.load_roles_and_positions()
    
    # Excluding position of EB, Faculty and SC-AG members
    for i in position:
        if(i.is_eb_member or i.is_faculty or i.is_sc_ag_eb_member):
            position=position.exclude(pk=i.pk)
    
    #load all insb members
    all_insb_members=Members.objects.all().order_by('position')
    
    
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
                permission_updated_for=Members.objects.get(ieee_id=ieee_id)
                messages.info(request,f"Permission Details Was Updated for {permission_updated_for.name}")
            
            else:
                messages.info(request,f"Something Went Wrong! Please Contact System Administrator about this issue")
        
        if request.POST.get('access_remove'):
            '''To remove record from data access table'''
            
            ieeeId=request.POST['access_ieee_id']
            if(renderData.MDT_DATA.remove_member_from_data_access(ieee_id=ieeeId)):
                messages.info(request,"Removed member from View Permission Controls")
                return redirect('membership_development_team:data_access')
            else:
                messages.info(request,"Something went wrong!")
                return redirect('membership_development_team:data_access')

                
        if request.POST.get('remove_member'):
            '''To remove member from team table'''
            try:
                Members.objects.filter(ieee_id=request.POST['remove_ieee_id']).update(team=None,position=Roles_and_Position.objects.get(id=13))
                try:
                    MDT_Data_Access.objects.filter(ieee_id=request.POST['remove_ieee_id']).delete()
                    messages.error(request,f"A Member with IEEE ID {request.POST['remove_ieee_id']} was Removed Successfully From Team")
                except MDT_Data_Access.DoesNotExist:
                    messages.error(request,"Something went wrong! Please, try again!")
                    return redirect('membership_development_team:data_access')
                return redirect('membership_development_team:data_access')
            except:
                pass
        
        if request.POST.get('update_data_access_member'):
            
            new_data_access_member_list=request.POST.getlist('member_select')
            
            if(len(new_data_access_member_list)>0):
                for ieeeID in new_data_access_member_list:
                    if(renderData.MDT_DATA.add_member_to_data_access(ieeeID)=="exists"):
                        messages.info(request,f"The member with IEEE Id: {ieeeID} already exists in the View Permission Controls Table")
                        return redirect('membership_development_team:data_access')
                    elif(renderData.MDT_DATA.add_member_to_data_access(ieeeID)==False):
                        messages.info(request,"Something Went wrong! Please try again")
                        return redirect('membership_development_team:data_access')
                    elif(renderData.MDT_DATA.add_member_to_data_access(ieeeID)==True):
                        messages.info(request,f"Member with {ieeeID} was added to the View Permission Controls table!")
                        return redirect('membership_development_team:data_access')

        if request.POST.get('add_member_to_team'):
            #get selected members
            members_to_add=request.POST.getlist('member_select1')
            #get position
            position=request.POST.get('position')
            for ieee_id in members_to_add:
                addMemberStatus=renderData.MDT_DATA.add_member_to_team(ieee_id,position)
                if(addMemberStatus):
                    add_to_data_access=renderData.MDT_DATA.add_member_to_data_access(ieee_id=ieee_id)
                    if(add_to_data_access):
                        messages.info(request,f"{ieee_id} has been successfully added as a member and also added to Data Access Table")
                    elif(add_to_data_access=="exists"):
                        messages.success(request,"A new Member was successfully added to the Team!")
                else:
                    messages.error(request,"Something went wrong! Please, Try again!")
            return redirect('membership_development_team:data_access')

    context={
        'data_access':data_access,
        'members':team_members,
        'insb_members':all_insb_members,
        'positions':position,
        
    }
    if(has_access):
        return render(request,'Manage Team/manage_team.html',context=context)
    else:
        return render(request,'access_denied.html')
    
@login_required
def site_registration_request_home(request):
    
    '''This loads data for site joining request'''
    # Getting all the requests for portal site
    get_requests=Portal_Joining_Requests.objects.all().order_by('application_status')
    #form link for site registration
    form_link=f"{request.META['HTTP_HOST']}/portal/membership_development_team/insb_site_registration_form"
    
    context={
        'requests':get_requests,
        'form_link':form_link
    }
    
    return render(request,'Site Registration/site_registration_home.html',context)

@login_required
def getSiteRegistrationRequestStats(request):
    '''This function returns stats of portal registration application and the stats'''
    if request.method=="GET":
        #loading all the unviewed request count
        notification_count=Portal_Joining_Requests.objects.filter(view_status=False).count()
        #counting the renewed requests
        accepted_count=Portal_Joining_Requests.objects.filter(application_status=True).count()
        #counting the pending requests
        pending_count=Portal_Joining_Requests.objects.filter(application_status=False).count()
        context={
            "labels":["Applications Not Yet Viewed","Total Pending Applications","Total Verified Applications"],
            "values":[notification_count,pending_count,accepted_count]
        }
        
        return JsonResponse(context)
        
        

@login_required
def site_registration_request_details(request,ieee_id):
    #gaining access data at first
    user=request.user
    has_access=Access_Render.system_administrator_superuser_access(user.username) or renderData.MDT_DATA.get_officials_access(request.user)
    
    '''Get the request data'''
    get_request=Portal_Joining_Requests.objects.get(ieee_id=ieee_id)
    
    #changing view Status
    Portal_Joining_Requests.objects.filter(ieee_id=ieee_id).update(view_status=True)
    
    dob = datetime.strptime(str(
        get_request.date_of_birth), "%Y-%m-%d").strftime("%Y-%m-%d")
    
    current_application=Portal_Joining_Requests.objects.get(ieee_id=ieee_id)
    next_application=Portal_Joining_Requests.objects.filter(pk__gt=current_application.ieee_id).first()
    
    if next_application:
        next_application_id=next_application.ieee_id
        has_next_request=True
    else:
        next_application_id=None
        has_next_request=False
    
    context={
        'request':get_request,
        'dob':dob,
        'next_application_id':next_application_id,
        'has_next_request':has_next_request
    }
    if request.method=="POST":
        if request.POST.get('register_to_database'):
            try:
                #Creating record for the new Member. If the IEEE already exists in the database it will already update that particualr record with new Information
                if(get_request.team==None):
                    new_member=Members(
                    ieee_id=get_request.ieee_id,
                    name=get_request.name,
                    nsu_id=get_request.nsu_id,
                    email_ieee=get_request.email_ieee,
                    email_nsu=get_request.email_nsu,
                    email_personal=get_request.email_personal,
                    major=get_request.major,
                    contact_no=get_request.contact_no,
                    home_address=get_request.home_address,
                    date_of_birth=get_request.date_of_birth,
                    gender=get_request.gender,
                    facebook_url=get_request.facebook_url,
                    linkedin_url=get_request.linkedin_url,
                    #if team=None then it will not create the record
                    position=Roles_and_Position.objects.get(id=get_request.position.id)

                    )
                    new_member.save()
                    #sending mails to MDT team officials to verify the request, primarily sent to their ieee mail
                    if(email_sending.send_email_on_site_registration_verification_to_user(request,new_member.name,new_member.email_personal)==False):
                        messages.info(request,"Couldn't Send Verification Email")
                        return redirect('membership_development_team:site_registration')

                    else:
                        messages.info(request,"User Notified via Email")
                        
                    #Updating application status
                    Portal_Joining_Requests.objects.filter(ieee_id=ieee_id).update(application_status=True)
                    messages.info(request,"Member Successfully Updated to the Main Database")
                    return redirect('membership_development_team:site_registration')
                    
                else:
                    #create with team id
                    new_member=Members(
                        ieee_id=get_request.ieee_id,
                        name=get_request.name,
                        nsu_id=get_request.nsu_id,
                        email_ieee=get_request.email_ieee,
                        email_nsu=get_request.email_nsu,
                        email_personal=get_request.email_personal,
                        major=get_request.major,
                        contact_no=get_request.contact_no,
                        home_address=get_request.home_address,
                        date_of_birth=get_request.date_of_birth,
                        gender=get_request.gender,
                        facebook_url=get_request.facebook_url,
                        linkedin_url=get_request.linkedin_url,
                        team=Teams.objects.get(id=get_request.team.id),
                        position=Roles_and_Position.objects.get(id=get_request.position.id)

                    )
                    new_member.save()

                    if(email_sending.send_email_on_site_registration_verification_to_user(request,new_member.name,new_member.email_personal)==False):
                        messages.info(request,"Couldn't Send Verification Email")
                    else:
                        messages.info(request,"User Notified via Email")
                
                    #Updating application status
                    Portal_Joining_Requests.objects.filter(ieee_id=ieee_id).update(application_status=True)
                    messages.info(request,"Member Successfully Updated to the Main Database")
                    return redirect('membership_development_team:site_registration')
            except:
                messages.info(request,"Something went wrong! Please try Again")
        if request.POST.get('delete_request'):
            #Deleting Member
            try:
                Portal_Joining_Requests.objects.filter(ieee_id=ieee_id).delete()
                messages.info(request,f"A Site Registration Application with IEEE ID: {ieee_id} was Deleted")
                return redirect('membership_development_team:site_registration')
            except:
                messages.info(request,"Sorry! Member Couldn't be Deleted")
    if(has_access):
        
        return render(request,'Site Registration/site_registration_application_details.html',context)
    else:
        return render(request,"access_denied.html")




from . models import Portal_Joining_Requests

def site_registration_form(request):
    load_all_teams=Teams.objects.all()
    positions=Roles_and_Position.objects.all()
    
    context={
        'team_data':load_all_teams,
        'positions':positions,
    }
    if request.method=="POST":
        
        if request.POST.get('apply'):
            messages.info(request,"Please wait a moment. The process might take some time.")
            #first check if the team is null or not
            if(request.POST.get('team')=="null"):
                try:
                    registration_request=Portal_Joining_Requests(
                        ieee_id=request.POST['ieee_id'],
                        name=request.POST['name'],
                        nsu_id=request.POST['nsu_id'],
                        email_ieee=request.POST['email_ieee'],
                        email_nsu=request.POST['email_nsu'],
                        email_personal=request.POST['email_personal'],
                        major=request.POST['major'],
                        contact_no=request.POST['contact_no'],
                        home_address=request.POST['home_address'],
                        date_of_birth=request.POST['date_of_birth'],
                        gender=request.POST['gender'],
                        facebook_url=request.POST['facebook_url'],
                        linkedin_url=request.POST['linkedin_url'],
                        team=None,
                        position=Roles_and_Position.objects.get(id=request.POST.get('position')) 
                    )
                    registration_request.save()
                    mdt_officials = renderData.MDT_DATA.load_officials_of_MDT()
                    for official in mdt_officials:
                        #sending mails to MDT team officials to verify the request, primarily sent to their personal mail
                        if(email_sending.send_emails_to_officials_upon_site_registration_request(request,registration_request.name,registration_request.ieee_id,registration_request.position,registration_request.team,official.name,official.email_personal)==False):
                            print("Email couldn't be sent")
                        else:
                            print(f"Email sent to {official.email_personal}")                    
                    return redirect('membership_development_team:confirmation')
                except:
                    messages.info(request,"Some Error Occured! Please contact the System Administrator")
                    return redirect('membership_development_team:site_registration_form')
            else:
                try:
                    registration_request=Portal_Joining_Requests(
                        ieee_id=request.POST['ieee_id'],
                        name=request.POST['name'],
                        nsu_id=request.POST['nsu_id'],
                        email_ieee=request.POST['email_ieee'],
                        email_nsu=request.POST['email_nsu'],
                        email_personal=request.POST['email_personal'],
                        major=request.POST['major'],
                        contact_no=request.POST['contact_no'],
                        home_address=request.POST['home_address'],
                        date_of_birth=request.POST['date_of_birth'],
                        gender=request.POST['gender'],
                        facebook_url=request.POST['facebook_url'],
                        linkedin_url=request.POST['linkedin_url'],
                        team=Teams.objects.get(id=request.POST.get('team')),
                        position=Roles_and_Position.objects.get(id=request.POST.get('position')) 
                    )
                    registration_request.save()
                    mdt_officials = renderData.MDT_DATA.load_officials_of_MDT()
                    for official in mdt_officials:
                        #sending mails to MDT team officials to verify the request, primarily sent to their personal mail
                        if(email_sending.send_emails_to_officials_upon_site_registration_request(request,registration_request.name,registration_request.ieee_id,registration_request.position,registration_request.team,official.name,official.email_personal)==False):
                            print("Email couldn't be sent")
                        else:
                            print(f"Email sent to {official.email_personal}")
                    return redirect('membership_development_team:confirmation')
                except:
                    messages.info(request,"Some Error Occured! Please contact the System Administrator")
                    return redirect('membership_development_team:site_registration_form')
    
    return render(request,'Site Registration/site_registration_form.html',context)
def confirmation_of_form_submission(request):
    return render(request,'confirmation.html')
