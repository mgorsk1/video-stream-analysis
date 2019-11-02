from app.analyzers.gatekeeper import Gatekeeper
from app.analyzers.whistleblower import PoliceWhistleblower
from app.video.prospectors.license_plate import LicensePlateProspector
from app.video.streamers.opencv import OpenCVCameraStreamer


class LicensePlateOpenCVGatekeeperAgent(Gatekeeper, LicensePlateProspector, OpenCVCameraStreamer):
    pass


class LicensePlateOpenCVPoliceWhistleblowerAgent(PoliceWhistleblower, LicensePlateProspector, OpenCVCameraStreamer):
    pass
