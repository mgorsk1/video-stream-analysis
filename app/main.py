from app.video import LocalCameraStream
from app.analyzers.whistleblower import Whistleblower


if __name__ == '__main__':
    with LocalCameraStream(30, 90, Whistleblower(5), **dict(general=dict(model='HP',
                                                                         id=17,
                                                                         location='Radom'))) as stream:
        pass




