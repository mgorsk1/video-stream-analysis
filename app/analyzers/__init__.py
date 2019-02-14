from abc import abstractmethod


class Analyzer:
    @abstractmethod
    def process(self,plate, confidence, image):
        raise NotImplementedError