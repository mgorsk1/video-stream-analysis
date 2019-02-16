import cv2

from openalpr import Alpr
from math import ceil
from os import environ
from time import strftime

from config import log, BASE_PATH


class CameraStream:
    def __init__(self, desired_fps, precision, analyzer, **kwargs):
        environ['TESSDATA_PREFIX'] = "{}/runtime/ocr/".format(BASE_PATH)
        environ['LD_LIBRARY_PATH'] = "/usr/include/"

        self.levels = [0, 50, 90, 100]
        self.names = ['low', 'medium', 'high']

        self.camera = cv2.VideoCapture(-1)
        self.precision = precision

        self.fps = ceil(self.camera.get(cv2.CAP_PROP_FPS) / desired_fps)
        self.analyzer = analyzer

        self.alpr = Alpr("eu", "{}/config/openalpr.conf".format(BASE_PATH), "{}/runtime/".format(BASE_PATH))

        self.alpr.set_top_n(10)
        self.alpr.set_default_region("pl")

        self.metadata = dict(kwargs)

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

    def get_raw_frame(self):
        res, frame = self.camera.read()

        return res, frame

    def analyze_frame(self):
        res, frame = self.get_raw_frame()
        recognition = self.alpr.recognize_ndarray(frame)
        results = recognition.get('results')

        result_set = list()
        if len(results) > 0:
            for result in results:
                plate, confidence = result.get('plate'), result.get('confidence')

                if confidence > self.precision:
                        candidates = [x.get('plate') for x in result.get('candidates')]

                        x1 = min([c.get('x') for c in result['coordinates']])
                        x2 = max([c.get('x') for c in result['coordinates']])

                        y1 = max([c.get('y') for c in result['coordinates']])
                        y2 = min([c.get('y') for c in result['coordinates']])

                        coordinates = [(x1, y1), (x2, y2)]

                        plate, confidence = result['candidates'][0].get('plate'), result['candidates'][0].get('confidence')

                        result_set.append(dict(coordinates=coordinates,
                                               plate=plate,
                                               confidence=confidence,
                                               candidates=candidates))

        for result in result_set:
            image = frame.copy()

            images = [frame, image]

            plate = result.get('plate')

            conf = result.get('confidence')
            conf_level = self.find_level(conf)

            cord1 = result.get('coordinates')[0]
            cord2 = result.get('coordinates')[1]

            candidates = result.get('candidates')

            for pic in images:
                cv2.rectangle(pic,
                              cord1,
                              cord2,
                              self.lineColors.get(conf_level),
                              2)

                info_to_print = ['Date: ' + strftime('%Y/%m/%d %H:%M:%S'), 'Plate: ' + plate, 'Confidence: ' + str(round(conf, 2))+'%']

                cv2.rectangle(pic, (cord1[0], cord1[1] + 5), (cord1[0] + 230, 5 + cord1[1] + (len(info_to_print) * 20)),
                              (255, 255, 255), -1)

                for i, info in enumerate(info_to_print):
                    cv2.putText(pic,
                                str(info),
                                (cord1[0], cord1[1]+20+(i*20)),
                                self.font,
                                self.fontScale,
                                (0, 0, 0),
                                self.lineType)

            log.debug('#recognized plate on #frame', dict(plate=plate, confidence=conf))

            additional_data = dict(metadata=self.metadata, candidates=candidates)
            self.analyzer.process(plate, conf, image, **additional_data)

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
        i = 0

        while True:
            i += 1

            results, frame = self.analyze_frame()

            if i % self.fps == 0:
                CameraStream.display(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    @staticmethod
    def display(frame):
        cv2.imshow("frame", frame)

