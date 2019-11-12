from abc import ABC, abstractmethod
from time import sleep, time

from app.config import log
from app.executors.base import FastTrackBaseExecutor


class BaseSuggester(FastTrackBaseExecutor, ABC):
    save_file_function = None

    def __init__(self, *args, **kwargs):
        super(BaseSuggester, self).__init__(*args, **kwargs)

        self.suggestion_duration = kwargs.get('suggester_suggestion_duration', 3)

    @property
    @abstractmethod
    def categories(self):
        pass

    @abstractmethod
    def _suggest(self, value, category):
        pass

    def _action(self, value, confidence, image, uuid, **kwargs):
        if not self.lock.locked():
            category = self.categories.get(value, 'n/a')

            log.info(f'#suggesting #{self.o}', extra=dict(value=value, category=category))

            self.acquire_lock()
            self._suggest(value, category)

            sleep(self.suggestion_duration)
            self.release_lock()

            log.info(f'#{self.o} #suggested', extra=dict(value=value))


class TrashCanSuggester(BaseSuggester):
    o = 'trash_can'

    def __init__(self, *args, **kwargs):
        super(TrashCanSuggester, self).__init__(*args, **kwargs)

    @property
    def categories(self):
        return dict(paper=':blue_heart:',
                    artificial=':yellow_heart:💛',
                    glass='💚:green_heart:', bio='🧡:heart:', mixed=':black_heart:🖤')

    def _suggest(self, value, category):
        # @todo make actual suggestion
        print(value, category, time())
