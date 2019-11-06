from app.config import BASE_PATH as BP
from app.config import log
from app.executors.base import BaseExecutor


class PushoverNotifier(BaseExecutor):
    def __init__(self, *args, **kwargs):
        super(PushoverNotifier, self).__init__(*args, **kwargs)

        notification_type = kwargs.get("notification_type", "default")

        with open(f'{BP}/resources/notifications/{notification_type}/title.txt', 'r') as f:
            self.notification_title = f.read()

        with open(f'{BP}/resources/notifications/{notification_type}/body.txt', 'r') as f:
            self.notification_body = f.read()

        self._setup_gcp()

    def _action(self, value, confidence, image, uuid, **kwargs):
        extra = dict(value=value, confidence=confidence, uuid=uuid)
        extra['kwargs'] = kwargs

        log.info("#notyfing pushover about #rascal", extra=extra)

        file = super(PushoverNotifier, self)._action(value, confidence, image, uuid, **kwargs)

        additional_data = dict(kwargs)
        additional_data.update(dict(gcp_file_url=file))

        camera_location = dict(kwargs).get('general', dict()).get('location', 'n/a')
        camera_id = dict(kwargs).get('general', dict()).get('id', 'n/a')

        data_for_template = dict(value=value,
                                 confidence=str(round(confidence, 3)) + '%',
                                 camera_id=camera_id,
                                 camera_location=camera_location)

        self.notify(self.notification_title.format(**data_for_template),
                    self.notification_body.format(**data_for_template),
                    file)

        log.info("#pushover notified about #rascal", extra=dict(value=dict(value=value)))
