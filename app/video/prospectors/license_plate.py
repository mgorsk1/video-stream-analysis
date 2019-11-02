from os import environ

from openalpr import Alpr

from app.config import log, BASE_PATH
from app.video.prospectors.base import BaseProspector

__all__ = ['LicensePlateProspector']


class LicensePlateProspector(BaseProspector):
    """
    LicensePlateProspector class is responsible for finding license plate objects in given stream of images.

    """

    def __init__(self, *args, **kwargs):
        print("LICENSE PLATE PROSPECTOR INIT")
        super(LicensePlateProspector, self).__init__(*args, **kwargs)

        environ['TESSDATA_PREFIX'] = "{}/resources/runtime/ocr/".format(BASE_PATH)
        environ['LD_LIBRARY_PATH'] = "/usr/include/"

        self.alpr = Alpr("eu", "{}/config/openalpr.conf".format(BASE_PATH), "{}/resources/runtime/".format(BASE_PATH))

        if not self.alpr.is_loaded():
            log.error("ALPR NOT LOADED")
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

            candidates = result.get('candidates')

            frame = self.format_result(frame, value, conf, cord1, cord2)
            image = self.format_result(image, value, conf, cord1, cord2)

            log.debug('#recognized value on #frame', dict(value=value, confidence=conf))

            additional_data = dict(metadata=dict(kwargs), candidates=candidates)

            self.pass_to_analyze(value, conf, image, **additional_data)

        return result_set, frame
