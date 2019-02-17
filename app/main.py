from app.video import CameraStreamOpenCV
from app.analyzers.whistleblower import Whistleblower


if __name__ == '__main__':
    camera_url = -1
    #camera_url = 'http://195.1.188.76/mjpg/video.mjpg'

    additional_data = dict(camera_url=camera_url, general=dict(model='HP', id=17, location='Radom'))

    with CameraStreamOpenCV(30, 90, Whistleblower(5), **additional_data) as stream:
        pass




