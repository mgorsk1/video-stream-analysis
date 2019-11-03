from app.analyzers.base import BaseAnalyzer
from app.config import log
from app.tools import format_key_active

__all__ = ['Brainless']


class Brainless(BaseAnalyzer):
    """
    Brainless class should be used when there is no grace period.
    """

    def __init__(self, *args, **kwargs):
        super(Brainless, self).__init__(*args, **kwargs)

    def _analyze(self, value, confidence, image, **kwargs):
        log.info("#starting #analysis", extra=dict(value=value, confidence=confidence))

        already_filed = self.tdb.get_val(format_key_active(value))

        if not already_filed:
            log.info("detection has not been filed yet", extra=dict(value=value))

            self.take_action(value, confidence, image, **dict(kwargs))
        else:
            log.info("detection already filed", extra=dict(value=value))

        log.info("#finished #analysis", extra=dict(value=value, confidence=confidence))
