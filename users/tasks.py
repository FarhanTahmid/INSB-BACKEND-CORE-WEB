from celery import shared_task
from membership_development_team.renderData import MDT_DATA
import logging

logger = logging.getLogger(__name__)

@shared_task
def running_task():
    logger.info('Task started')
    inst = MDT_DATA()
    inst.check_active_members()
    logger.info('Task ended')

def testing():
    running_task.apply_async()
    