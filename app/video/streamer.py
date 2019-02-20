from abc import abstractmethod
from math import ceil
import cv2


class Stream:
    def __init__(self, desired_fps, prospector, display_frame=True, **kwargs):
        self.camera = None
        self.fps = None

        self.prospector = prospector
        self.desired_fps = desired_fps

        self.display_frame = display_frame

        self.metadata = dict(kwargs)

    @abstractmethod
    def get_raw_frame(self):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError

    def __enter__(self):
        self.run()

    def run(self):
        i = 0

        while True:
            i += 1

            results, frame = self.get_raw_frame()

            if i % self.fps == 0:
                if self.prospector:
                    results, frame = self.prospector.search(frame, **self.metadata)

                if self.display_frame:
                    self.display(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def display(self, frame):
        cv2.imshow(self.window_name, frame)


class CameraStreamOpenCV(Stream):
    camera_properties = {k: v for k, v in globals().get("cv2", dict()).__dict__.items() if k.startswith('CAP_PROP_')}

    def __init__(self, *args, **kwargs):
        super(CameraStreamOpenCV, self).__init__(*args, **kwargs)

        camera_url = dict(kwargs).get('camera_url', -1)

        self.camera = cv2.VideoCapture(camera_url)

        camera_metadata = dict()

        for k, v in self.camera_properties.items():
            try:
                val = self.camera.get(v)
                if val > -1:
                    camera_metadata[k] = val
            except:
                pass

        self.metadata.update(dict(camera=camera_metadata))

        camera_fps = self.camera.get(cv2.CAP_PROP_FPS)

        if self.desired_fps >= camera_fps:
            self.desired_fps = camera_fps

        self.fps = ceil(camera_fps/self.desired_fps)

        self.window_name = 'video-analysis'

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def __exit__(self, exc_type, exc_value, traceback):
        self.camera.release()
        cv2.destroyAllWindows()

        self.alpr.unload()

    def get_raw_frame(self):
        res, frame = self.camera.read()

        return res, frame
