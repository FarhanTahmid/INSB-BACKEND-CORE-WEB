from django.core.mail import send_mail
import uuid
from django.conf import settings

class EmailHandler:
    
    def sendForgetPasswordLinkToUserViaEmail(request,user_email,username):
        
        '''Sends an email to the users email (The personal email they provided when they signed up for the system) with link to restore their password'''
        
        token=str(uuid.uuid4()) #this token is randomly generated with uuid
        
        subject="Password Reset Link - IEEE NSU SB Portal"
        
        site_domain = request.META['HTTP_HOST'] #gets the domain name
        
        message=f"Dear user,\nYour password reset link is:\n{site_domain}/users/reset_password/{username}/{token}/\nPlease do not share this link with any other individuals.\nThank you.\n\nThis message was automatically generated fromt the portal site of IEEE NSU SB."
        
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
    

        