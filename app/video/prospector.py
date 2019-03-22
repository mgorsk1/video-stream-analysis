from abc import abstractmethod
from os import environ
from threading import Thread
from time import strftime

import pickle
import cv2
from openalpr import Alpr

from app.config import log, BASE_PATH


class Prospector:
    def __init__(self, precision, analyzer):
        self.precision = precision
        self.analyzer = analyzer

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.fontScale = 0.5

        self.fontColors = dict(low=(0, 0, 255), medium=(255, 0, 0), high=(0, 255, 0))

        self.lineType = 2
        self.lineColors = self.fontColors

        self.levels = [0, 50, 90, 100]
        self.names = ['low', 'medium', 'high']

    @abstractmethod
    def search(self, frame, **kwargs):
        raise NotImplementedError

    def find_level(self, value):
        result = None

        if len(self.levels) != len(self.names) + 1:
            return ""

        for i in range(len(self.levels) - 1):
            if value > self.levels[i] and value <= self.levels[i + 1]:
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

        print('format', upper_left, bottom_right)
        print('frame', frame_upper_left, frame_bottom_right)

        # background for text
        cv2.rectangle(frame, frame_upper_left, frame_bottom_right, (255, 255, 255), -1)

        for i, info in enumerate(info_to_print):
            cv2.putText(frame, str(info), (upper_left[0], upper_left[1] + 20 + (i * 20)), self.font, self.fontScale,
                        (0, 0, 0), self.lineType)

        return frame

    def pass_to_analyze(self, value, conf, image, **kwargs):
        log.info("starting thread for #analysis of #image",
                 extra=dict(target=self.analyzer.analyze, args=(value, conf, image)))

        t = Thread(target=self.analyzer.analyze, args=(value, conf, image,), kwargs=dict(kwargs))

        t.start()


class LicensePlateProspector(Prospector):
    def __init__(self, *args, **kwargs):
        super(LicensePlateProspector, self).__init__(*args, **kwargs)

        environ['TESSDATA_PREFIX'] = "{}/resources/runtime/ocr/".format(BASE_PATH)
        environ['LD_LIBRARY_PATH'] = "/usr/include/"

        self.alpr = Alpr("eu", "{}/config/openalpr.conf".format(BASE_PATH), "{}/resources/runtime/".format(BASE_PATH))

        if not self.alpr.is_loaded():
            print("ALPR NOT LOADED")
            exit(1)

        self.alpr.set_top_n(10)
        self.alpr.set_default_region("pl")

    def search(self, frame, **kwargs):
        frame = frame.copy()
        clean_frame = frame.copy()

        recognition = self.alpr.recognize_ndarray(frame)
        results = recognition.get('results')

        result_set = list()

        if len(results) > 0:
            for result in results:
                value, confidence = result.get('plate'), result.get('confidence')

                if confidence > self.precision:
                    candidates = [x.get('plate') for x in result.get('candidates')]

                    x1 = min([c.get('x') for c in result['coordinates']])
                    x2 = max([c.get('x') for c in result['coordinates']])

                    y1 = max([c.get('y') for c in result['coordinates']])
                    y2 = min([c.get('y') for c in result['coordinates']])

                    coordinates = [(x1, y1), (x2, y2)]

                    value, confidence = result['candidates'][0].get('plate'), result['candidates'][0].get('confidence')

                    result_set.append(
                        dict(coordinates=coordinates, value=value, confidence=confidence, candidates=candidates))

        for result in result_set:
            image = clean_frame.copy()

            value = result.get('value')

            conf = result.get('confidence')

            cord1 = result.get('coordinates')[0]
            cord2 = result.get('coordinates')[1]

            print(cord1, cord2)

            candidates = result.get('candidates')

            frame = self.format_result(frame, value, conf, cord1, cord2)
            image = self.format_result(image, value, conf, cord1, cord2)

            log.debug('#recognized value on #frame', dict(value=value, confidence=conf))

            additional_data = dict(metadata=dict(kwargs), candidates=candidates)

            self.pass_to_analyze(value, conf, image, **additional_data)

        return result_set, frame


class PeopleProspector(Prospector):
    def __init__(self, *args, **kwargs):
        super(PeopleProspector, self).__init__(*args, **kwargs)

        self.face_classifier = cv2.CascadeClassifier(
            '{}/resources/cascades/data/haarcascade_frontalface_alt2.xml'.format(BASE_PATH))

        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read("{}/resources/recognizers/face-trainer.yml".format(BASE_PATH))

        self.labels = dict()

        face_labels_dir = "{}/resources/pickles/".format(BASE_PATH)
        face_labels_file = "{}/face-labels.pickle".format(face_labels_dir)

        with open(face_labels_file, 'rb') as f:
            og_labels = pickle.load(f)
            self.labels = {v: k for k, v in og_labels.items()}

    def search(self, frame, **kwargs):
        frame = frame.copy()
        clean_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        result_set = list()

        matches = self.face_classifier.detectMultiScale(clean_frame, scaleFactor=1.5, minNeighbors=5)

        for (x, y, w, h) in matches:
            roi_gray = clean_frame[y:y + h, x:x + w]

            value, conf = self.recognizer.predict(roi_gray)

            value = self.labels[value]

            conf_level = self.find_level(conf)

            if conf >= self.precision:
                frame = self.format_result(frame, value, conf, (x, y + h), (x + w, y))

                result_set.append(dict(value=value, confidence=conf))

                self.pass_to_analyze(value, conf, frame)

        return result_set, frame
