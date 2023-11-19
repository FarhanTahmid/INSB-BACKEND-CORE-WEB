from datetime import datetime
from .models import SystemErrors
import logging

class ErrorHandling:
    
    logger=logging.getLogger(__name__)
    
    def saveSystemErrors(error_name,error_traceback):
        try:
            new_error=SystemErrors.objects.create(
                date_time=datetime.now(),
                error_name=error_name,
                error_traceback=error_traceback
            )
            new_error.save()
        except:
            ErrorHandling.logger.error("An error occurred at {datetime}".format(datetime=datetime.now()), exc_info=True)
