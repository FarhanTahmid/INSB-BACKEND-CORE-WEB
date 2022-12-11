from . models import Renewal_requests,Renewal_Sessions

def get_renewal_session_name(pk):
    session_name=Renewal_Sessions.objects.filter(id=pk).values('session_name')
    return (session_name[0]['session_name'])
def get_renewal_session_id(session_name):
    session_id=Renewal_Sessions.objects.filter(session_name=session_name).values('id')
    id=0
    for i in range(len(session_id)):
        id=session_id[i]['id']
    return id