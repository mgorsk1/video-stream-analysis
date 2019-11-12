from app.agents import *

AGENTS = dict(parking=LicensePlateOpenCVVigilanteAgent,
              gate=LicensePlateOpenCVGatekeeperAgent,
              trash=TrashOpenCVSuggestAgent)

a = 'trash'


def run():
    camera_url = -1
    # camera_url = 'http://195.1.188.76/mjpg/video.mjpg'

    agent = AGENTS.get(a)

    agent = agent(prospector_precision=70,
                  analyzer_grace_period=0,
                  executor_reset_after=5,
                  streamer_desired_fps=2,
                  streamer_display_frame=False,
                  streamer_camera_metadata=dict(camera_url=camera_url,
                                                general=dict(model='HP', id=17,
                                                             location='Radom')))

    agent.run()


if __name__ == '__main__':
    run()
