from app.agents import LicensePlateOpenCVVigilanteAgent


def run():
    camera_url = -1
    # camera_url = 'http://195.1.188.76/mjpg/video.mjpg'

    # interpreter = LicensePlateProspector(60, Whistleblower(8 * 60 * 60, grace_period=5))
    #
    # additional_data = ))
    #
    # stream = CameraStreamOpenCV(30, interpreter, True, **additional_data)
    #
    # stream.run()

    agent = LicensePlateOpenCVVigilanteAgent(
        **dict(grace_period=5,
               desired_fps=5,
               precision=92,
               display_frame=False,
               reset_after=30,
               notification_type='parking_violation',
               camera_metadata=dict(camera_url=camera_url,
                                    general=dict(model='HP', id=17,
                                                 location='Radom'))))

    agent.run()


if __name__ == '__main__':
    run()
