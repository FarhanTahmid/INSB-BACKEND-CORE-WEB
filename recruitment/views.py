from django.shortcuts import render, redirect
from django.db import DatabaseError, IntegrityError, InternalError
from django.http import HttpResponseServerError, HttpResponseBadRequest, HttpResponse
from recruitment.models import recruitment_session, recruited_members
from users.models import Members
from . import renderData
from django.contrib.auth.decorators import login_required
from . forms import StudentForm
from . models import recruited_members
from django.contrib import messages
import datetime
from django.core.exceptions import ObjectDoesNotExist
import xlwt,csv
from django.db.utils import IntegrityError
from membership_development_team.renderData import MDT_DATA
from membership_development_team import email_sending
from system_administration.render_access import Access_Render
# Create your views here.


@login_required
def recruitment_home(request):
    '''Loads all the recruitment sessions present in the database
        this can also register a recruitment session upon data entry
        this passes all the datas into the template file    
    '''
    
        
    numberOfSessions = renderData.Recruitment.loadSession()
    if request.method == "POST":
        session_name = request.POST["recruitment_session"]
        session_time=datetime.datetime.now()
        try:
            add_session = recruitment_session(session=session_name,session_time=session_time)
            add_session.save()
        except DatabaseError:
            return DatabaseError
    return render(request, 'recruitment_homepage.html', numberOfSessions)


@login_required
def recruitee(request, pk):
    '''This function is responsible for getting all the members registered in a particular
    recruitment session. Loads all the datas and show them
    '''
    #check the users view access
    user=request.user
    has_access=(MDT_DATA.recruitment_session_view_access_control(user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username))
    
    getSession = renderData.Recruitment.getSession(session_id=pk)
    getMemberCount = renderData.Recruitment.getTotalNumberOfMembers(int(pk))
    getRecruitedMembers = renderData.Recruitment.getRecruitedMembers(
        session_id=pk)

    context = {
        'pk':pk,
        'memberCount': getMemberCount,
        'session': getSession,
        'members': getRecruitedMembers,
    }
    if(has_access):
        return render(request, 'session_recruitees.html', context=context)
    else:
        return render(request,'access_denied.html')

@login_required
def recruitee_details(request,session_id,nsu_id):
    """Preloads all the data of the recruitees who are registered in the particular session, here we can edit and save the data of the recruitee"""
    #Checking user access
    user=request.user
    has_access=(MDT_DATA.recruited_member_details_view_access(user.username) or Access_Render.system_administrator_superuser_access(user.username) or Access_Render.system_administrator_staffuser_access(user.username))
    try:

        data = renderData.Recruitment.getRecruitedMemberDetails(nsu_id=nsu_id,session_id=session_id)
        # this parses the date in -DD-MM-YY Format for html
        # this dob does not change any internal data, it is used just to convert the string type from database to load in to html
        dob = datetime.datetime.strptime(str(
            data.date_of_birth), "%Y-%m-%d").strftime("%Y-%m-%d")
        address=data.home_address
        
     
    except ObjectDoesNotExist:
        # if object doesnot exist...
        messages.info(request, "Member does not exist!")
    except:
        # goes to recruitment home if list_index_out_of bound occures
        return redirect('recruitment:recruitment_home')

    # Passing data to the template
    session=data.session_id
    context = {
        'session': data.session_id,
        'data': data,
        'dob': dob,
        'address':address,
    }

    if request.method == "POST":
        
        
        # # this is used to update the recruited member details
        # # Upon entering IEEE id this registers members to the main database of members
        if request.POST.get('save_edit'):
            
        #     # checks the marked check-boxes
            cash_payment_status = False
            if request.POST.get('cash_payment_status'):
                cash_payment_status = True
            ieee_payment_status = False
            if request.POST.get('ieee_payment_status'):
                ieee_payment_status = True
            # Collecting all infos
            info_dict = {
                'first_name': request.POST['first_name'],
                'middle_name': request.POST['middle_name'],
                'last_name': request.POST['last_name'],
                'contact_no': request.POST['contact_no'],
                'date_of_birth': request.POST['date_of_birth'],
                'email_personal': request.POST['email_personal'],
                'facebook_url': request.POST['facebook_url'],
                'home_address': request.POST['home_address'],
                'major': request.POST['major'], 'graduating_year': request.POST['graduating_year'],
                'ieee_id': request.POST['ieee_id'],
                'recruited_by': request.POST['recruited_by'],
                'cash_payment_status': cash_payment_status,
                'ieee_payment_status': ieee_payment_status,
                'comment':request.POST['comment']
            }
            

             # Getting returned values and handling the exceptions

            if (renderData.Recruitment.updateRecruiteeDetails(nsu_id=nsu_id, values=info_dict) == "no_ieee_id"):
                messages.info(
                    request, "Please Enter IEEE ID if you have completed payment")
                return redirect('recruitment:recruitee_details', session_id,nsu_id)
            elif (renderData.Recruitment.updateRecruiteeDetails(nsu_id=nsu_id, values=info_dict) == IntegrityError):
                messages.info(
                    request, "There is already a member registered with this IEEE ID")
                return redirect('recruitment:recruitee_details',session_id, nsu_id)
            elif (renderData.Recruitment.updateRecruiteeDetails(nsu_id=nsu_id, values=info_dict) == InternalError):
                messages.info(request, "A Server Error Occured!")
                return redirect('recruitment:recruitee_details',session_id ,nsu_id)
            elif (renderData.Recruitment.updateRecruiteeDetails(nsu_id=nsu_id, values=info_dict)):
                messages.info(request, "Information Updated")
                return redirect('recruitment:recruitee_details', session_id,nsu_id)
            else:
                messages.info(
                    request, "Something went wrong. Please Try again")
                return redirect('recruitment:recruitee_details', session_id,nsu_id)

        # ##### DELETING RECRUITEES#######
        if request.POST.get('delete_member'):
            
            # if(renderData.Recruitment.deleteMember(nsu_id=nsu_id)=="both_database"):
            #     messages.info(request,f"Member Deleted Successfully from recruitment process and also from INSB Database with the id {nsu_id}")
            if (renderData.Recruitment.deleteMember(nsu_id=nsu_id,session_id=data.session_id) == ObjectDoesNotExist):
                messages.info(
                    request, f"The member with the id {nsu_id} was deleted!")
                return redirect('recruitment:recruitee', session)
            elif (renderData.Recruitment.deleteMember(nsu_id=nsu_id,session_id=data.session_id)):
                
                return redirect('recruitment:recruitee', session)
            else:
                messages.info(request, f"Something went wrong! Try again!")
                return redirect('recruitment:recruitee', session)
            
            

        # ##### REGISTERING MEMBER IN INSB DATABASE####
        if request.POST.get("register_member"):
            
            getMember = recruited_members.objects.filter(nsu_id=nsu_id).values(
                'ieee_id',
                'first_name', 'middle_name', 'last_name',
                'nsu_id',
                'email_personal',
                'major',
                'contact_no',
                'home_address',
                'date_of_birth',
                'gender',
                'facebook_url',
                'session_id',
                'ieee_payment_status',
                'recruitment_time'
            )
            print(type(getMember[0]['recruitment_time']))
            # Registering member to the main database
            try:
                newMember = Members(
                    ieee_id=int(getMember[0]['ieee_id']),
                    name=getMember[0]['first_name'] + " " +
                    getMember[0]['middle_name']+" " +
                    getMember[0]['last_name'],
                    nsu_id=getMember[0]['nsu_id'],
                    email_personal=getMember[0]['email_personal'],
                    major=getMember[0]['major'],
                    contact_no=getMember[0]['contact_no'],
                    home_address=getMember[0]['home_address'],
                    date_of_birth=getMember[0]['date_of_birth'],
                    gender=getMember[0]['gender'],
                    facebook_url=getMember[0]['facebook_url'],
                    session=recruitment_session.objects.get(id=int(getMember[0]['session_id']))
                )
                newMember.save()
                messages.info(request, "Member Updated in INSB Database")
                return redirect('recruitment:recruitee_details',session_id, nsu_id)
            except IntegrityError:
                messages.info(
                    "An Error Occured! The member is already registered in INSB Database or you have not entered IEEE ID of the member!")
                return redirect('recruitment:recruitee_details',session_id, nsu_id)
            # except:
            #     messages.info(
            #         request, "Something went wrong! Please Try again!")
            #     return redirect('recruitment:recruitee_details', nsu_id)
    if(has_access):
        return render(request, "recruitee_details.html", context=context)
    else:
        return render(request,'access_denied.html')

@login_required
def recruit_member(request, session_name):
    getSessionId = renderData.Recruitment.getSessionid(
        session_name=session_name)
    form = StudentForm
    context = {
        'form': form,
        'session_name': session_name,
        'session_id': getSessionId['session'][0]['id']
    }

    # this method is for the POST from the recruitment form

    if request.method == "POST":
        
       
            cash_payment_status = False
            if request.POST.get("cash_payment_status"):
                cash_payment_status = True
            ieee_payment_status = False
            if request.POST.get("ieee_payment_status"):
                ieee_payment_status = True
            time = datetime.datetime.now()
            # getting all data from form and registering user upon validation
            if(recruited_members.objects.filter(nsu_id=request.POST['nsu_id'],session_id=getSessionId['session'][0]['id']).exists()):
                messages.info(request,f"Member with NSU ID: {request.POST['nsu_id']} is already registered in the database under this same recruitment session!")
                return redirect('recruitment:recruit_member',session_name)
            else:
                try:

                    recruited_member = recruited_members(
                        nsu_id=request.POST['nsu_id'],
                        first_name=request.POST['first_name'],
                        middle_name=request.POST['middle_name'],
                        last_name=request.POST['last_name'],
                        contact_no=request.POST['contact_no'],
                        date_of_birth=request.POST['date_of_birth'],
                        email_personal=request.POST['email_personal'],
                        gender=request.POST['gender'],
                        facebook_url=request.POST['facebook_url'],
                        home_address=request.POST['home_address'],
                        major=request.POST.get('major'),
                        graduating_year=request.POST['graduating_year'],
                        session_id=getSessionId['session'][0]['id'],
                        recruitment_time=time,
                        recruited_by=request.POST['recruited_by'],
                        cash_payment_status=cash_payment_status,
                        ieee_payment_status=ieee_payment_status
                    )
                    recruited_member.save()  # Saving the member to the database
                    
                    #send an email now to the recruited member
                    email_status=email_sending.send_email_to_recruitees_upon_recruitment(
                        recruited_member.first_name,recruited_member.nsu_id,recruited_member.email_personal,session_name)
                    
                    if(email_status)==False:
                        messages.info(request,"The system could not send email to the recruited member due to some errors! Please contact the system administrator")
                    elif(email_status):
                        messages.info(request,"E-mail sent to the newly recruited member!")
                        
                    return redirect('recruitment:recruitee', getSessionId['session'][0]['id'])

                except IntegrityError:  # Checking if same id exist and handling the exception
                    messages.info(
                        request, f"Member with NSU ID: {request.POST['nsu_id']} is already registered in the database!")
                    return render(request, "membership_form.html", context=context)

                # except:  # Handling all errors
                #     messages.info(request, "Something went Wrong! Please try again")
                #     return render(request, "membership_form.html", context=context)
                
                

    else:
        return render(request, "membership_form.html", context=context)


@login_required
def generateExcelSheet(request, session_name):
    '''This method generates the excel files for different sessions'''
    date=datetime.datetime.now()
    response = HttpResponse(
        content_type='application/ms-excel')  # eclaring content type for the excel files
    response['Content-Disposition'] = f'attachment; filename=Recruitment Session - {session_name}---' +\
        str(date.strftime('%m/%d/%Y')) + \
        '.xls'  # making files downloadable with name of session and timestamp
    # adding encoding to the workbook
    workBook = xlwt.Workbook(encoding='utf-8')
    # opening an worksheet to work with the columns
    workSheet = workBook.add_sheet(f'Recruitment-{session_name}')

    # generating the first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    # Defining columns that will stay in the first row
    columns = ['NSU ID', 'First Name', 'Middle Name', 'Last Name', 'Email (personal)', 'Contact No', 'IEEE ID', 'Gender', 'Date Of Birth', 'Facebook Url',
               'Address', 'Major', 'Graduating Year', 'Recruitment Time', 'Recruited By', 'Cash Payment Status', 'IEEE Payment Status']

    # Defining first column
    for column in range(len(columns)):
        workSheet.write(row_num, column, columns[column], font_style)

    # reverting font style to default
    font_style = xlwt.XFStyle()

    # getting the session to find members recruited in that particular session
    getSession = renderData.Recruitment.getSessionid(session_name=session_name)

    # getting all the values of members as rows with same session
    rows = recruited_members.objects.filter(session_id=getSession['session'][0]['id']).values_list('nsu_id',
                                                                                                   'first_name', 'middle_name', 'last_name',
                                                                                                   'email_personal',
                                                                                                   'contact_no',
                                                                                                   'ieee_id',
                                                                                                   'gender',
                                                                                                   'date_of_birth',
                                                                                                   'facebook_url',
                                                                                                   'home_address',
                                                                                                   'major', 'graduating_year',
                                                                                                   'recruitment_time',
                                                                                                   'recruited_by',
                                                                                                   'cash_payment_status',
                                                                                                   'ieee_payment_status'
                                                                                                   )

    for row in rows:

        row_num += 1
        for col_num in range(len(row)):
            workSheet.write(row_num, col_num, str(row[col_num]), font_style)
    workBook.save(response)
    return (response)
