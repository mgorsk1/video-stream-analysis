from abc import ABC, abstractmethod

import cv2

__all__ = ['BaseStreamer']


class BaseStreamer(ABC):
    def __init__(self, *args, **kwargs):
        super(BaseStreamer, self).__init__()

        self.camera = None
        self.fps = None

        self.desired_fps = kwargs.get('desired_fps', 15)

        self.display_frame = kwargs.get('display_frame', False)

        self.metadata = kwargs.get('camera_metadata')

    @abstractmethod
    def get_raw_frame(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __enter__(self):
        self.run()

    def search(self, frame, **kwargs):
        return frame, None

    def run(self):
        i = 0

        while True:
            i += 1

            results, frame = self.get_raw_frame()

            if i % self.fps == 0:
                results, frame = self.search(frame, **self.metadata)

                if self.display_frame:
                    self.display(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def display(self, frame):
        cv2.imshow(self.window_name, frame)
