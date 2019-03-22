from app.video.streamer import CameraStreamOpenCV
from app.video.prospector import LicensePlateProspector, PeopleProspector
from app.analyzers.whistleblower import Whistleblower


def run():
    camera_url = -1
    # camera_url = 'http://195.1.188.76/mjpg/video.mjpg'

    interpreter = LicensePlateProspector(60, Whistleblower(8 * 60 * 60, grace_period=5))

    additional_data = dict(camera_url=camera_url, general=dict(model='HP', id=17, location='Radom'))

    stream = CameraStreamOpenCV(30, interpreter, True, **additional_data)

    stream.run()


if __name__ == '__main__':
    run()



