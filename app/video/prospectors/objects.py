from json import loads
from typing import Dict, Tuple, Optional

import cv2
from google.cloud import vision
from google.cloud.vision import types

from app.config import BASE_PATH, log
from app.video.prospectors.base import BaseProspector


class ObjectGCPProspector(BaseProspector):
    """
    ObjectGCPProspector class is responsible for recognizing objects in stream using ML models from Google Cloud.
    """

    def __init__(self, *args, **kwargs):
        super(ObjectGCPProspector, self).__init__(*args, **kwargs)

        with open(f'{BASE_PATH}/resources/gcp_objects/class-descriptions.json', 'r') as f:
            self.labels = loads(f.read())

        self.client = vision.ImageAnnotatorClient()

    def search(self, frame, **kwargs):
        result_set = list()

        frame_bytes = cv2.imencode('.jpg', frame)[1].tostring()

        img = types.Image(content=frame_bytes)

        x = 25
        y = 25
        h = 10
        w = 200

        # Performs label detection on the image file
        response = self.client.label_detection(image=img)
        annotations = {l.description: round(l.score * 100, 2) for l in response.label_annotations}

        log.debug("#received #annotations", extra=dict(annotations=annotations))

        result = self._get_best_pick(annotations)

        if result is not None:
            description, category, confidence = [result.get(x) for x in ['description', 'category', 'confidence']]

            if confidence >= self.precision:
                frame = self.format_result(frame, f'{category} ({description})', confidence, (x, y + h), (x + w, y))

                result_set.append(dict(value=category,
                                       confidence=confidence,
                                       image=frame,
                                       metadata=dict(original_object=description)))

            return result_set, frame
        else:
            return dict(), frame

    def _get_best_pick(self, values: Dict[str, float]) -> Optional[Tuple[str, str, float]]:
        import operator

        values_sorted = sorted(values.items(), key=operator.itemgetter(1), reverse=True)

        for description, score in values_sorted:
            category = self.labels.get(description)

            if category:
                result = dict(description=description, category=category, confidence=score)

                log.info("#found #best #pick", extra=dict(result=result))

                return result

        return None
