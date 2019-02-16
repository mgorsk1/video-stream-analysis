import cv2

from abc import abstractmethod
from json import dumps
from time import time
from uuid import uuid4
from inflection import underscore
from os import getenv, environ, remove
from requests import post, HTTPError
from threading import Thread
from google.cloud import storage

from app.database import ResultDatabase, TemporaryDatabase
from config import log, BASE_PATH


class Executor:
    def __init__(self, reset_after):
        environ['GOOGLE_APPLICATION_CREDENTIALS'] = "{}/config/gcp/key.json".format(BASE_PATH)

        self.reset_after = reset_after

        self.index_name = underscore(self.__class__.__name__)
        self.rdb = ResultDatabase("localhost", 9200, self.index_name)
        self.tdb = TemporaryDatabase("localhost", 6379)

        self.pushover_config = dict(APP_TOKEN=getenv("PUSHOVER_APP_TOKEN"), USER_KEY=getenv("PUSHOVER_USER_KEY"))

    @abstractmethod
    def action(self, plate, confidence, image, **kwargs):
        raise NotImplementedError

    def run(self, plate, confidence, image, **kwargs):
        run_uuid = uuid4()

        value = dumps(dict(time_added=time(), confidence=confidence)).encode('utf-8')

        if self.reset_after <= 0:
            self.tdb.set_key(plate + ':Y', value)
        else:
            self.tdb.set_key(plate+':Y', value, ex=self.reset_after)

        self.take_action(plate, confidence, image, run_uuid, **dict(kwargs))

    def take_action(self, plate, confidence, image, uuid, **kwargs):
        if not self.rdb.check_if_exists(self.index_name, plate, False):
            log.info("#plate does not exist in result #database", extra=dict(plate=plate))
            if not self.rdb.check_if_exists('plate', plate, True):
                log.info("#similar #plate does not exist in result #database", extra=dict(plate=plate))
                if not self.rdb.check_if_exists('candidates', plate, False):
                    log.info("#plate does not exist amongst candidates in #database", extra=dict(plate=plate))

                    t = Thread(target=self.action, args=(plate, confidence, image, uuid, ), kwargs=dict(kwargs))
                    t.start()

                    log.info("#notification send about plate", extra=dict(plate=plate, confidence=confidence))
                else:
                    log.info("#plate existed amongst candidates in #database", extra=dict(plate=plate))
            else:
                log.info("#plate matched another #similar plate in #database", extra=dict(plate=plate))
        else:
            log.info("#plate existed in #database", extra=dict(plate=plate))

        pass

    def notify_pushover(self, title, message, url):
        """
        Send request to pushover_notify API with data:

        token (required) - your application"s API token
        user (required) - the user/group key (not e-mail address) of your user (or you), viewable when logged into our dashboard (often referred to as USER_KEY in our documentation and code examples)
        message (required) - your message
        Some optional parameters may be included:
        attachment - an image attachment to send with the message; see attachments for more information on how to upload files
        device - your user"s device name to send the message directly to that device, rather than all of the user"s devices (multiple devices may be separated by a comma)
        title - your message"s title, otherwise your app"s name is used
        url - a supplementary URL to show with your message
        url_title - a title for your supplementary URL, otherwise just the URL is shown
        priority - send as -2 to generate no notification/alert, -1 to always send as a quiet notification, 1 to display as high-priority and bypass the user"s quiet hours, or 2 to also require confirmation from the user
        sound - the name of one of the sounds supported by device clients to override the user"s default sound choice
        timestamp - a Unix timestamp of your message"s date and time to display to the user, rather than the time your message is received by our API

        :param title: title for message
        :param message: message
        :param url: optional url to pass
        :return: -
        """
        def notify():
            request_data = dict(token=self.pushover_config.get("APP_TOKEN", ""),
                                user=self.pushover_config.get("USER_KEY", ""),
                                message=message,
                                device="pw-bd-project-funct-pushover_notify",
                                title=title,
                                url=url)

            try:
                result = post("https://api.pushover.net/1/messages.json", data=request_data)
            except:
                raise HTTPError

        t = Thread(target=notify())
        t.start()

    def save_image_to_gcp(self, plate, image, uuid):
        tmp_file = Executor.save_image_locally(plate, image, uuid, 'tmp', 'png')

        filename = "{}_{}.png".format(plate, uuid)

        client = Executor._get_storage_client()
        bucket = client.bucket(self.index_name)
        blob = bucket.blob(filename)

        blob.upload_from_filename(tmp_file, content_type="image/png")

        remove(tmp_file)

        return blob.public_url

    @staticmethod
    def save_image_locally(plate, image, uuid, folder, ext):
        filename = "{}_{}.{}".format(plate, uuid, ext)

        full_path = "{}/{}/{}".format(BASE_PATH, folder, filename)

        cv2.imwrite(full_path, image)

        log.info("#saved #image", extra=dict(filePath=full_path))

        return full_path

    @staticmethod
    def _get_storage_client():
        return storage.Client(project=getenv('GCP_PROJECT_ID'))
