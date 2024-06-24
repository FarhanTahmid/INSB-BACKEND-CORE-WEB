from datetime import datetime

from system_administration.models import General_Log


class System_Logs:
    
    def save_logs(object, message):

        '''This function saves the general log whenever needed'''
        
        #getting current time
        current_datetime = datetime.now()
        current_time = current_datetime.strftime('%d-%m-%Y %I:%M:%S %p')
        #getting the log
        log_details = General_Log.objects.get(log_of = object)
        #updating log details
        log_details.log_details[current_time+f"_{log_details.update_number}"] = message
        log_details.update_number+=1
        log_details.save()