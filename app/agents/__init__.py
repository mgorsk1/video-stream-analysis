from app.analyzers.gatekeeper import Gatekeeper
from app.analyzers.whistleblower import Vigilante
from app.executors.notify import PoliceNotifier
from app.executors.open import GateOpener
from app.video.prospectors.license_plate import LicensePlateProspector
from app.video.streamers.opencv import OpenCVCameraStreamer


class LicensePlateOpenCVGatekeeperAgent(GateOpener, Gatekeeper, LicensePlateProspector, OpenCVCameraStreamer):
    pass


class LicensePlateOpenCVVigilanteAgent(PoliceNotifier, Vigilante, LicensePlateProspector, OpenCVCameraStreamer):
    pass
