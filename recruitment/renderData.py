#this file is solely responsible for collecting all the related data for recruitment site
from . models import recruitment_session
class Recruitment:
    def __init__(self) -> None:
        pass
    def loadSession():
        return {'sessions':recruitment_session.objects.all().values()} #returns a dictionary which contains session dataa
        