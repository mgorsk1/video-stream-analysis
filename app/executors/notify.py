from app.config import log
from app.executors.base import BaseExecutor


class PoliceNotifier(BaseExecutor):
    def __init__(self, *args, **kwargs):
        super(PoliceNotifier, self).__init__(*args, **kwargs)

    def _action(self, value, confidence, image, uuid, **kwargs):
        file = super(PoliceNotifier, self)._action(value, confidence, image, uuid)

        title_temvalue = "{cl} Parking Violation! Registration number: {rn}"
        message_temvalue = """
        Camera location: {cl}
        Camera ID: {cid}
        Registration number: {rn}
        Confidence: {cf}
        """

        additional_data = dict(kwargs)
        additional_data.update(dict(gcp_file_url=file))

        camera_location = dict(kwargs).get('metadata', dict()).get('general', dict()).get('location', 'n/a')
        camera_id = dict(kwargs).get('metadata', dict()).get('general', dict()).get('id', 'n/a')

        self.notify(title_temvalue.format(cl=camera_location, rn=value), message_temvalue.format(rn=value,
                                                                                                 cf=str(
                                                                                                     round(confidence,
                                                                                                           3)) + '%',
                                                                                                 cid=camera_id,
                                                                                                 cl=camera_location),
                    file)

        log.info("#police notified about #rascal", extra=dict(value=value))
