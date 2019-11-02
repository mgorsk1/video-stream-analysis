import pickle

import cv2

from app.config import BASE_PATH
from app.video.prospectors.base import BaseProspector

__all__ = ['PeopleProspector']


class PeopleProspector(BaseProspector):
    """
    PeopleProspector class is responsible for finding peoples faces in given stream of images.


    """

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

            value, confidence = self.recognizer.predict(roi_gray)

            value = self.labels[value]

            conf_level = self.find_level(confidence)

            if confidence >= self.precision:
                frame = self.format_result(frame, value, conf_level, (x, y + h), (x + w, y))

                result_set.append(dict(value=value, confidence=confidence))

                self.pass_to_analyze(value, confidence, frame)

        return result_set, frame
