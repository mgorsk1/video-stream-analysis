from app.video.streamer import CameraStreamOpenCV
from app.video.prospector import  LicensePlateProspector
from app.analyzers.whistleblower import Whistleblower


def run():
    camera_url = -1
    # camera_url = 'http://195.1.188.76/mjpg/video.mjpg'

    interpreter = LicensePlateProspector(90, Whistleblower(5, 8*60*60))

    additional_data = dict(camera_url=camera_url, general=dict(model='HP', id=17, location='Radom'))

    with CameraStreamOpenCV(30, interpreter, **additional_data) as stream:
        pass


if __name__ == '__main__':
    run()



