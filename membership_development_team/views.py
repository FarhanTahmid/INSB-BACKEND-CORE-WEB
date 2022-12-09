from django.shortcuts import render,redirect
from django.db import DatabaseError, IntegrityError, InternalError
from users.models import Members
from port.models import Roles_and_Position
from recruitment import renderData
from django.db import connections
from django.contrib.auth.decorators import login_required
from . models import Renewal_Sessions
from django.http import HttpResponse
import datetime
import xlwt

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
    sessions=Renewal_Sessions.objects.all()
    context={
        'sessions':sessions
    }
    if request.method=="POST":
        #MUST PERFORM TRY CATCH
        #Creating and inserting the data of the session
        try:
            session_name=request.POST['renewal_session']
            session_time=datetime.datetime.now()
            add_session=Renewal_Sessions.objects.create(session_name,session_time)
            add_session.save()
        except DatabaseError:
            return DatabaseError
        return redirect('membership_renewal')
    return render(request,'renewal.html',context)

@login_required
def renewal_session_data(request,pk):
    '''This view function loads all data for the renewal session including the members registered'''
    return render(request,'renewal_session.html')

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