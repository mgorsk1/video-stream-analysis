from app.analyzers.base import BaseAnalyzer
from app.analyzers.gatekeeper import Gatekeeper
from app.analyzers.vigilante import Vigilante
from app.executors.notify import PushoverNotifier
from app.executors.open import GateOpener
from app.executors.suggest import TrashCanSuggester
from app.video.prospectors.license_plate import LicensePlateProspector
from app.video.prospectors.objects import ObjectGCPProspector
from app.video.streamers.opencv import OpenCVCameraStreamer


class LicensePlateOpenCVGatekeeperAgent(GateOpener, Gatekeeper, LicensePlateProspector, OpenCVCameraStreamer):
    pass


class LicensePlateOpenCVVigilanteAgent(PushoverNotifier, Vigilante, LicensePlateProspector, OpenCVCameraStreamer):
    pass


class TrashOpenCVSuggestAgent(TrashCanSuggester, BaseAnalyzer, ObjectGCPProspector, OpenCVCameraStreamer):
    pass
