from abc import ABC, abstractmethod
from time import sleep

from app.config import log
from app.executors.base import FastTrackBaseExecutor


class BaseSuggester(ABC, FastTrackBaseExecutor):
    save_file_function = None

    def __init__(self, *args, **kwargs):
        super(BaseSuggester, self).__init__(*args, **kwargs)

        self.suggestion_duration = kwargs.get('suggestion_duration', 2)

    @abstractmethod
    def _suggest(self, value):
        pass

    @property
    @abstractmethod
    def categories(self):
        pass

    def _action(self, value, confidence, image, uuid, **kwargs):
        super(BaseSuggester, self)._action(value, confidence, image, uuid)

        self.suggest(value)

    def suggest(self, value):
        category = self.categories.get(value, 'n/a')
        log.info(f"#suggesting #{self.o}", extra=dict(value=value, category=category))

        self._suggest(value)

        sleep(self.suggestion_duration)

        log.info(f"#{self.o} #suggested", extra=dict(value=value))


class TrashCanSuggester(BaseSuggester):
    def __init__(self, *args, **kwargs):
        super(TrashCanSuggester, self).__init__(*args, **kwargs)

    @property
    def categories(self):
        return dict(paper=":blue_heart:",
                    artificial=":yellow_heart:💛",
                    glass="💚:green_heart:", bio="🧡:heart:", mixed=":black_heart:🖤")

    def _suggest(self, value):
        # @todo make actual suggestion
        pass
