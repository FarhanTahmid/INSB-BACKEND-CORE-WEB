from port.models import Teams



class Branch:
    
    def load_teams():
        
        '''This function returns all the teams in the database'''
        
        teams=Teams.objects.all().values('id','team_name') #returns a list of dictionaryies with the id and team name
        return teams