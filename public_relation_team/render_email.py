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
        if to_email_list[0] is not '':
            for email in to_email_list:
                if email=="general_members":
                    # get general member emails
                    pass
                elif email=="all_officers":
                    # get all officers email
                    branch_officers=Branch.load_all_officers_of_branch()
                    print("Trying to get branch officers")
                    for officer in branch_officers:
                        print(officer.email_personal)
                elif email=="eb_panel":
                    # get all eb panel email
                    pass
                elif email=="excom_branch":
                    # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                    pass
                elif email=="scag_eb":
                    # get all the society, chapters and AG EBS
                    pass
        
        # Get all the cc_email_list
        cc_email_final_list=[]
        # check first if the list has null value in list, it means that there was no email selected
        if cc_email_list[0] is not '':
            for email in to_email_list:
                if email=="general_members":
                    # get general member emails
                    pass
                elif email=="all_officers":
                    # get all officers email
                    pass
                elif email=="eb_panel":
                    # get all eb panel email
                    pass
                elif email=="excom_branch":
                    # get all the email of branch excom. this means all branch EBs + SC & AG chairs(only)
                    pass
                elif email=="scag_eb":
                    # get all the society, chapters and AG EBS
                    pass
        
        # get all bcc_email_list
        bcc_email_final_list=[]
        # check first if the list has null value in list, it means that there was no email selected
        if bcc_email_list[0] is not '':
            for email in to_email_list:
                if email=="general_members":
                    # get general member emails
                    pass
                elif email=="all_officers":
                    # get all officers email
                    pass
                elif email=="eb_panel":
                    # get all eb panel email
                    pass
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
        
        