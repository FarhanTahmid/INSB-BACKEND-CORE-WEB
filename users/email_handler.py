from django.core.mail import send_mail
import uuid
from django.conf import settings

class EmailHandler:
    
    def sendForgetPasswordLinkToUserViaEmail(request,user_email,username):
        
        '''Sends an email to the users email (The personal email they provided when they signed up for the system) with link to restore their password'''
        
        token=str(uuid.uuid4()) #this token is randomly generated with uuid
        
        subject="Password Reset Link - IEEE NSU SB Portal"
        
        site_domain = request.META['HTTP_HOST'] #gets the domain name
        
        message=f"Dear user,\nYour password reset link is:\n{site_domain}/portal/users/reset_password/{username}/{token}/\nPlease do not share this link with any other individuals.\nThank you.\n\nThis message was automatically generated fromt the portal site of IEEE NSU SB."
        
        email_from = settings.EMAIL_HOST_USER
        
        recipient_list = [user_email]
        try:
            send_mail(
                    subject, message, email_from, recipient_list
                )
            mail_sent=True
        except Exception as e:
            mail_sent=False
            print(e)
        
        return token,mail_sent #the function returns the token generated and if the mail is sent or not.
    
    def send_email_for_signup(request,member):
        '''sends an email to the user with an unique token to signup in the database'''
        # randomly generating token
        token=str(uuid.uuid4())
        site_domain=request.META['HTTP_HOST'] #gets the domain name
        
        subject="Signup Link - IEEE NSU SB Portal"
        
        message=f"""
        Dear {member.name},
        Your Portal signup link is:
        {site_domain}/portal/users/signup/{member.ieee_id}/{token}/
        Please, do not share this link anywhere else.
        
        Thank you.
        
        This message was generated from IEEE NSU SB Portal System. If you are not supposed to recieve this email, please contact our Website Development Team.
        
        """
        email_from = settings.EMAIL_HOST_USER

        recipient_list = [member.email_personal]

        try:
            send_mail(
                    subject, message, email_from, recipient_list
                )
            mail_sent=True
        except Exception as e:
            mail_sent=False
            print(e)
        
        return token,mail_sent

        