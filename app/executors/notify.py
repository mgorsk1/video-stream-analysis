from . import Executor
from config import log


class PoliceNotifier(Executor):
    def action(self, plate, confidence, image, uuid, **kwargs):
        title_template = "{cl} Parking Violation! Registration number: {rn}"
        message_template = """
        Camera location: {cl}
        Camera ID: {cid}
        Registration number: {rn}
        Confidence: {cf}
        """

        cloud_file = self.save_image_to_gcp(plate, image, uuid)

        additional_data = dict(kwargs)
        additional_data.update(dict(gcp_file_url=cloud_file))

        self.rdb.index_result(plate, confidence, uuid, **additional_data)

        camera_location = dict(kwargs).get('metadata', dict()).get('general',dict()).get('location', 'n/a')
        camera_id = dict(kwargs).get('metadata', dict()).get('general',dict()).get('id', 'n/a')

        self.notify_pushover(title_template.format(cl=camera_location,
                                                   rn=plate),
                             message_template.format(rn=plate,
                                                     cf=str(round(confidence, 3))+'%',
                                                     cid=camera_id,
                                                     cl=camera_location),
                             cloud_file)

        log.info("#police notified about #rascal", extra=dict(plate=plate))
