import csv
import django
from users.models import Members
from recruitment.models import recruited_members
import datetime
from django.db import connection
class Registration:
    def __init__(self) -> None:
        pass
    def populateMembersDataThroughExcel():
        '''This function is used to populate members in the MEMBERS table through CSV files'''
        with open("./DATA/TEST-MEMBER_DATA.csv",'r') as file_registered_members:
            fileReader=csv.reader(file_registered_members)
            for row in fileReader:
                if(row[0]=="ï»¿IEEE ID"):
                    continue
                else:
                    try:
                        addMember=Members(ieee_id=row[0],
                                        name=row[1],
                                        nsu_id=row[2],
                                        email_ieee=row[3],
                                        email_personal=row[4],
                                        contact_no=row[5],
                                        home_address=row[6],
                                        date_of_birth=row[7],
                                        gender=row[8],
                                        facebook_url=row[9]
                                        )
                        addMember.save()
                    except django.db.utils.IntegrityError:
                        continue
                    finally:
                        connection.close()
    
    def populate_recruitment_data_table_from_csv():
        '''THIS BLOCK OF CODE CONTAINS CODE TO MANUALLY INPUT DATA FOR A RECRUITMENT SESSION FROM A CSV FILE '''
        with open("./DATA/Fall_2020_Recruited_Members.csv", 'r') as file_registered_members:
                fileReader = csv.reader(file_registered_members)
                for row in fileReader:
                    if ("ï»¿" in row[0]):
                        continue
                    else:
                        
                            addMember = recruited_members(
                                                nsu_id=row[0],
                                                first_name=row[1],
                                                middle_name=row[2],
                                                last_name=row[3],
                                                date_of_birth=datetime.datetime.strptime(row[4], "%m/%d/%Y").strftime("%Y-%m-%d"),
                                                email_personal=row[5],
                                                gender=row[6],
                                                home_address=row[7],
                                                major=row[8],
                                                graduating_year=row[9],
                                                session_id=row[10],
                                                recruited_by=row[11],
                                                cash_payment_status=row[12],
                                                ieee_payment_status=row[13]
                                                )
                            addMember.save()
            
                    