from central_branch.renderData import Branch
class PRT_Email_System:
    
    def get_all_selected_emails_from_backend(single_emails,to_email_list,cc_email_list,bcc_email_list):
        
        # At first seperate the emails of single emails seperated by commas
        single_emails_final_list=[]
        
        substrings = single_emails.split(',')
        
        for email in substrings:
            # Trim leading and trailing whitespaces
            single_emails_final_list.extend(email.split())
 
        
        # Get the emails of to_email_list 
        to_email_final_list=[]
        # check first if the list has null value in list, it means that there was no email selected
        if to_email_list[0] != '':
            for email in to_email_list:
                if email=="general_members":
                    # get general member emails
                    general_members=Branch.load_all_active_general_members_of_branch()
                    for member in general_members:
                        to_email_final_list.append(member.email_nsu)
                elif email=="all_officers":
                    # get all officers email
                    branch_officers=Branch.load_all_officers_of_branch()
                    for officer in branch_officers:
                        to_email_final_list.append(officer.email_nsu)
                        
                elif email=="eb_panel":
                    # get all eb panel email
                    eb_panel=Branch.load_branch_eb_panel()
                    for eb in eb_panel:
                        to_email_final_list.append(eb.email_ieee)
                        
                elif email=="excom_branch":
                    # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                    pass
                elif email=="scag_eb":
                    # get all the society, chapters and AG EBS
                    pass
        
        # Get all the cc_email_list
        cc_email_final_list=[]
        # check first if the list has null value in list, it means that there was no email selected
        if cc_email_list[0] != '':
            for email in cc_email_list:
                if email=="general_members":
                    # get general member emails
                    general_members=Branch.load_all_active_general_members_of_branch()
                    for member in general_members:
                        cc_email_final_list.append(member.email_nsu)
                elif email=="all_officers":
                    # get all officers email
                    branch_officers=Branch.load_all_officers_of_branch()
                    for officer in branch_officers:
                        cc_email_final_list.append(officer.email_nsu)
                elif email=="eb_panel":
                    # get all eb panel email
                    eb_panel=Branch.load_branch_eb_panel()
                    for eb in eb_panel:
                        cc_email_final_list.append(eb.email_ieee)
                elif email=="excom_branch":
                    # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                    pass
                elif email=="scag_eb":
                    # get all the society, chapters and AG EBS
                    pass
        
        # get all bcc_email_list
        bcc_email_final_list=[]
        # check first if the list has null value in list, it means that there was no email selected
        if bcc_email_list[0] != '':
            for email in bcc_email_list:
                if email=="general_members":
                    # get general member emails
                    general_members=Branch.load_all_active_general_members_of_branch()
                    for member in general_members:
                        bcc_email_final_list.append(member.email_nsu)
                elif email=="all_officers":
                    # get all officers email
                    branch_officers=Branch.load_all_officers_of_branch()
                    for officer in branch_officers:
                        bcc_email_final_list.append(officer.email_nsu)
                elif email=="eb_panel":
                    # get all eb panel email
                    eb_panel=Branch.load_branch_eb_panel()
                    for eb in eb_panel:
                        bcc_email_final_list.append(eb.email_ieee)
                elif email=="excom_branch":
                    # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                    pass
                elif email=="scag_eb":
                    # get all the society, chapters and AG EBS
                    pass
        
        
        print("After processing:")
        print(f"Single Emails:{single_emails_final_list}")
        print(f"To Emails:{to_email_final_list}")
        print(f"Cc Emails:{cc_email_final_list}")
        print(f"Bcc Emails:{bcc_email_final_list}")
        
        