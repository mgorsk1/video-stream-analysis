from app.video import CameraStream
from app.analyzers.whistleblower import Whistleblower


if __name__ == '__main__':
    with CameraStream(30, Whistleblower(10)) as stream:
        pass




