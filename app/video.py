import cv2

from openalpr import Alpr
from math import ceil
from os import path, environ
from uuid import uuid4

BASE_PATH = path.dirname(__file__) + "/.."


class CameraStream:
    def __init__(self, desired_fps, handler, analyze=None):
        if not analyze:
            self.analyze = False
        else:
            self.analyze = True

        self.handler = handler

        # if not display:
        #     self.display = False
        # else:
        #     self.display = True

        environ['TESSDATA_PREFIX'] = "{}/runtime/ocr/".format(BASE_PATH)
        environ['LD_LIBRARY_PATH'] = "/usr/include/"

        self.levels = [0, 50, 90, 100]
        self.names = ['low', 'medium', 'high']

        self.camera = cv2.VideoCapture(-1)

        self.fps = ceil(self.camera.get(cv2.CAP_PROP_FPS) / desired_fps)

        self.alpr = Alpr("eu", "{}/config/openalpr.conf".format(BASE_PATH), "{}/runtime/".format(BASE_PATH))

        self.alpr.set_top_n(5)
        self.alpr.set_default_region("pl")

        if not self.alpr.is_loaded():
            print("ALPR NOT LOADED")
            exit(1)

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontScale = 0.5

        self.fontColors = dict(low=(0, 0, 255), medium=(255, 0, 0), high=(0, 255, 0))

        self.lineType = 2
        self.lineColors = self.fontColors

    def __enter__(self):
        self.run()

    def __exit__(self, exc_type, exc_value, traceback):
        self.camera.release()
        cv2.destroyAllWindows()

        self.alpr.unload()

    def raw_frame(self):
        res, frame = self.camera.read()

        return res, frame

    def analyzed_frame(self):
        res, frame = self.raw_frame()

        recognition = self.alpr.recognize_ndarray(frame)
        results = recognition.get('results')

        result_set = list()

        good_guess = False

        if len(results) > 0:
            for result in results:
                for x in result['candidates']:
                    plate, confidence = x.get('plate'), x.get('confidence')

                    if confidence > 93:
                        good_guess = True
                        break

                if good_guess:
                    x1 = min([c.get('x') for c in result['coordinates']])
                    x2 = max([c.get('x') for c in result['coordinates']])

                    y1 = max([c.get('y') for c in result['coordinates']])
                    y2 = min([c.get('y') for c in result['coordinates']])

                    coordinates = [(x1, y1), (x2, y2)]

                    plate, confidence = result['candidates'][0].get('plate'), result['candidates'][0].get('confidence')

                    result_set.append(dict(coordinates=coordinates, plate=plate, confidence=confidence))

        for result in result_set:
            plate = result.get('plate')

            conf = result.get('confidence')
            conf_level = self.find_level(conf)

            cord1 = result.get('coordinates')[0]
            cord2 = result.get('coordinates')[1]

            cv2.rectangle(frame,
                          cord1,
                          cord2,
                          self.lineColors.get(conf_level),
                          2)

            cv2.putText(frame,
                        '{} ({})'.format(plate, round(conf, 4)),
                        cord2,
                        self.font,
                        self.fontScale,
                        self.lineColors.get(conf_level),
                        self.lineType)

            self.handler.process(plate, conf, frame)

        if len(result_set) > 0:
            CameraStream.save_frame(frame)

        return result_set, frame

    def find_level(self, value):
        result = None

        if len(self.levels) != len(self.names) + 1:
            return ""

        for i in range(len(self.levels)-1):
            if value > self.levels[i] and value <= self.levels[i+1]:
                result = self.names[i]
                break

        return result

    def run(self):
        mode = self.analyzed_frame if self.analyze else self.raw_frame

        i = 0

        while True:
            i += 1

            results, frame = mode()

            if i % self.fps == 0:
                CameraStream.display(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    @staticmethod
    def display(frame):
        cv2.imshow("frame", frame)

    @staticmethod
    def save_frame(frame):
        cv2.imwrite("{}/output/{}.png".format(BASE_PATH, uuid4()), frame)
