from central_branch.models import Events

class PRT_Data:

    def publish_event_to_website(publish_to_web,event_id) -> bool:
        try:
            Events.objects.filter(id=event_id).update(publish_in_main_web=publish_to_web)
            return True
        except Events.DoesNotExist:
            return False
