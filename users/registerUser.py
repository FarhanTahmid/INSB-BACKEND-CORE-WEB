import csv
import psycopg2
import django
from users.models import Members
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
            
                