from math import ceil

import cv2

from app.video.streamers.base import BaseStreamer

__all__ = ['OpenCVCameraStreamer']


class OpenCVCameraStreamer(BaseStreamer):
    camera_properties = {k: v for k, v in globals().get('cv2', dict()).__dict__.items() if k.startswith('CAP_PROP_')}

    def __init__(self, *args, **kwargs):
        super(OpenCVCameraStreamer, self).__init__(*args, **kwargs)

        camera_url = dict(kwargs).get('camera_url', -1)

        self.camera = cv2.VideoCapture(camera_url)

        camera_metadata = dict()

        for k, v in self.camera_properties.items():
            try:
                val = self.camera.get(v)
                if val > -1:
                    camera_metadata[k] = val
            except Exception:
                pass

        self.metadata.update(dict(camera=camera_metadata))

        camera_fps = self.camera.get(cv2.CAP_PROP_FPS)

        if self.desired_fps >= camera_fps:
            self.desired_fps = camera_fps

        self.fps = ceil(camera_fps / self.desired_fps)

        self.window_name = 'video-analysis'

        if self.display_frame:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def __exit__(self, exc_type, exc_value, traceback):
        self.camera.release()
        cv2.destroyAllWindows()

        self.alpr.unload()

    def get_raw_frame(self):
        res, frame = self.camera.read()

        return res, frame
