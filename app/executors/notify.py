from app.config import log
from . import Executor


class PoliceNotifier(Executor):
    def action(self, value, confidence, image, uuid, **kwargs):
        title_temvalue = "{cl} Parking Violation! Registration number: {rn}"
        message_temvalue = """
        Camera location: {cl}
        Camera ID: {cid}
        Registration number: {rn}
        Confidence: {cf}
        """

        cloud_file = self.save_image_to_gcp(value, image, uuid)

        additional_data = dict(kwargs)
        additional_data.update(dict(gcp_file_url=cloud_file))

        self.rdb.index_result(value, confidence, uuid, **additional_data)

        camera_location = dict(kwargs).get('metadata', dict()).get('general',dict()).get('location', 'n/a')
        camera_id = dict(kwargs).get('metadata', dict()).get('general',dict()).get('id', 'n/a')

        self.notify_pushover(title_temvalue.format(cl=camera_location, rn=value), message_temvalue.format(rn=value,
                                                     cf=str(round(confidence, 3))+'%',
                                                     cid=camera_id,
                                                     cl=camera_location),
                             cloud_file)

        log.info("#police notified about #rascal", extra=dict(value=value))
