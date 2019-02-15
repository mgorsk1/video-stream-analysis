from app.video import CameraStream
from app.analyzers.whistleblower import Whistleblower


if __name__ == '__main__':
    with CameraStream(30, 90, Whistleblower(10), **dict(cameraModel='HP')) as stream:
        pass




