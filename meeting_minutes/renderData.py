from . models import team_meeting_minutes, branch_meeting_minutes

class team_mm_info:

    def load_all_team_mm():
        ' ' ' This function loads all the meeting minutes of the team' ' '

        team_mm_list=team_meeting_minutes.objects.all().values('team_mm_id','team_mm_names')
        return team_mm_list

    def add_mm_to_team(team_id,team_meeting_title):
        ' ' ' This function adds new meeting minutes of the team' ' '
        team_meeting_minutes.objects.filter(team_id=team_id).update(team_meeting_title)

class branch_mm_info:

    def load_all_branch_mm():
        ' ' ' This function loads all the meeting minutes of the branch' ' '

        branch_mm_list=branch_meeting_minutes.objects.all().values('branch_mm_id','branch_mm_names')
        return branch_mm_list

    def add_mm_to_branch(branch_or_society_id,branch_or_society_meeting_title):
        ' ' ' This function adds new meeting minutes of the team' ' '
        branch_meeting_minutes.objects.filter(branch_or_society_id=branch_or_society_id).update(branch_or_society_meeting_title)  