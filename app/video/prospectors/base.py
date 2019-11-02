from abc import ABC, abstractmethod
from time import strftime

import cv2

__all__ = ['BaseProspector']


class BaseProspector(ABC):
    """
    BaseProspector class is responsible for analyzing stream of images and search for particular objects within them.

    Once found - it's passed to analysis.

    """

    def __init__(self, *args, **kwargs):
        super(BaseProspector, self).__init__(*args, **kwargs)

        self.precision = kwargs.get('precision')

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontScale = 0.5

        self.fontColors = dict(low=(0, 0, 255), medium=(255, 0, 0), high=(0, 255, 0))

        self.lineType = 2
        self.lineColors = self.fontColors

        self.levels = [0, 50, 90, 100]
        self.names = ['low', 'medium', 'high']

    @abstractmethod
    def search(self, frame, **kwargs):
        pass

    def analyze(self, value, confidence, image, **kwargs):
        return None

    def find_level(self, value):
        result = None

        if len(self.levels) != len(self.names) + 1:
            return ""

        for i in range(len(self.levels) - 1):
            if self.levels[i] < value <= self.levels[i + 1]:
                result = self.names[i]
                break

        return result

    def format_result(self, frame, value, confidence, upper_left, bottom_right):
        frame = frame.copy()

        conf_level = self.find_level(confidence)

        # mark found area
        cv2.rectangle(frame, upper_left, bottom_right, self.lineColors.get(conf_level), 2)

        info_to_print = ['Date: ' + strftime('%Y/%m/%d %H:%M:%S'), 'Result: ' + str(value),
                         'Confidence: ' + str(round(confidence, 3)) + '%']

        frame_upper_left = upper_left
        frame_bottom_right = (upper_left[0] + 230, upper_left[1] + (20 * len(info_to_print)) + 5)

        # background for text
        cv2.rectangle(frame, frame_upper_left, frame_bottom_right, (255, 255, 255), -1)

        for i, info in enumerate(info_to_print):
            cv2.putText(frame, str(info), (upper_left[0], upper_left[1] + 20 + (i * 20)), self.font, self.fontScale,
                        (0, 0, 0), self.lineType)

        return frame
