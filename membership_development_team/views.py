from django.shortcuts import render,redirect
from django.db import DatabaseError, IntegrityError, InternalError
from users.models import Members
from port.models import Roles_and_Position
from recruitment import renderData
from django.db import connections
from django.contrib.auth.decorators import login_required
from . models import Renewal_Sessions,Renewal_requests
from . import renewal_data
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseServerError
import datetime
import xlwt
from django.contrib import messages


# Create your views here.
def md_team_homepage(request):
    return render(request,'md_team_homepage.html')

@login_required
def members_list(request):
    '''This function is responsible to display all the member data in the page'''
    members=Members.objects.order_by('position')
    totalNumber=Members.objects.all().count()
    context={'members':members,'totalNumber':totalNumber}
          
    return render(request,'insb_member_list.html',context=context)

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
    get_renewal_requests=Renewal_requests.objects.filter(session_id=session_id).values('name','email_personal','contact_no',)
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
def renewal_request_details(request,pk,name):
    '''This function loads the datas for particular renewal requests'''
    renewal_request_details=Renewal_requests.objects.filter(name=name).values('name','email_personal','ieee_account_password','ieee_renewal_check','pes_renewal_check','ras_renewal_check','ias_renewal_check','wie_renewal_check','transaction_id','renewal_status','contact_no','comment','official_comment')
    #changing the notification status
    Renewal_requests.objects.filter(name=name).update(view_status=True)
    
    context={
        'name':name,
        'details':renewal_request_details,
    }
    if request.method=="POST":
        if(request.POST.get('renew_button')):
            print(Renewal_requests.objects.filter(name=name,session_id=int(pk)).values('name'))
        if(request.POST.get('delete_button')):
            print("Delete button")
        if(request.POST.get('update_comment')):
            updated_comment=request.POST['official_comment']
            print(updated_comment)
            print("Update Comment")
            
    return render(request,"renewal_request_details.html",context=context)
    

@login_required
def generateExcelSheet(request):
    '''This method generates the excel files for different sessions'''
    response = HttpResponse(
        content_type='application/ms-excel')  # eclaring content type for the excel files
    response['Content-Disposition'] = f'attachment; filename=Member List - ' +\
        str(datetime.datetime.now()) + \
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