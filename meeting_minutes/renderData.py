from . models import team_meeting_minutes, branch_meeting_minutes

class team_mm_info:

    def load_all_team_mm():
        team_mm_list=team_meeting_minutes.objects.all().values('team_mm_id','team_mm_names')
        return team_mm_list

    