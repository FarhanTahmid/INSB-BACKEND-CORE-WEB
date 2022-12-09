from . models import Renewal_requests,Renewal_Sessions

def get_renewal_session_name(pk):
    session_name=Renewal_Sessions.objects.filter(id=pk).values('session_name')
    return (session_name[0]['session_name'])