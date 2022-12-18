from users.models import Members

class MDT_DATA:
    
    def get_member_data(ieee_id):
        member_data=Members.objects.get(ieee_id=ieee_id)
        return {
            'ieee_id':member_data.ieee_id,
            'name':member_data.name,
            'nsu_id':member_data.nsu_id,
            'email_ieee':member_data.email_ieee,
            'email_personal':member_data.email_personal,
            'major':member_data.major,
            'contact_no':member_data.contact_no,
            'home_address':member_data.home_address,
            'date_of_birth':member_data.date_of_birth,'gender':member_data.gender,
            'facebook_url':member_data.facebook_url,
            'team':member_data.team,
            'position':member_data.position,
            'session':member_data.session,
            'last_renewal':member_data.last_renewal,        
        }
    