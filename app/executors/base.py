from json import dumps
from os import getenv, environ, remove
from time import time
from uuid import uuid4

import cv2
from google.cloud import storage
from inflection import underscore
from requests import post, HTTPError

from app.config import log, BASE_PATH, config
from app.dbs.result import ResultDatabase
from app.dbs.temporary import TemporaryDatabase
from app.tools import format_key_active


class BaseExecutor:
    save_file_function = 'save_image_to_gcp'

    def __init__(self, *args, **kwargs):
        super(BaseExecutor, self).__init__(*args, **kwargs)

        self.reset_after = kwargs.get('reset_after', 60)

        self.bucket_folder_name = underscore(self.__class__.__name__)
        self.index = 'video-analysis-{}'.format(self.bucket_folder_name)

        self.rdb = ResultDatabase(config.get('RDB_HOST'),
                                  config.get('RDB_PORT'), self.index,
                                  **dict(db_user=config.get('RDB_USER'),
                                         db_pass=getenv('RDB_PASS'),
                                         db_scheme=config.get('RDB_SCHEME')))

        self.tdb = TemporaryDatabase(config.get('TDB_HOST'), config.get('TDB_PORT'), **dict(db_pass=getenv('TDB_PASS')))

        self.save_file = None

        self.bucket = None

        self.pushover_config = None

    def take_action(self, value, confidence, image, **kwargs):
        run_uuid = uuid4()

        attributes = dumps(dict(time_added=time(), confidence=confidence)).encode('utf-8')

        self.action(value, confidence, image, run_uuid, **dict(kwargs))

        self.tdb.set_val(format_key_active(value), attributes, ex=max(self.reset_after, 1))

    def action(self, value, confidence, image, uuid, **kwargs):
        exact_match = self.rdb.get_val(value, field='value', ago=self.reset_after, fuzzy=False)
        if exact_match is None:
            log.info("#value does not exist in result #database", extra=dict(value=value))
            fuzzy_match = self.rdb.get_val(value, field='value', ago=self.reset_after, fuzzy=False)
            if fuzzy_match is None:
                log.info("#similar #value does not exist in result #database", extra=dict(value=value))
                candidates_match = self.rdb.get_val(value, field='candidates', ago=self.reset_after, fuzzy=False)
                if candidates_match is None:
                    log.info("#value does not exist amongst candidates in #database", extra=dict(value=value))

                    self._action(value, confidence, image, uuid, **dict(kwargs))

                    log.info("#notification send about value", extra=dict(value=value, confidence=confidence))
                else:
                    log.info("#value existed amongst candidates in #database", extra=dict(value=value))
            else:
                log.info("#value matched another #similar value in #database", extra=dict(value=value))
        else:
            log.info("#value existed in #database", extra=dict(value=value))

        pass

    def save_image_to_gcp(self, value, image, uuid):
        if self.bucket is None:
            self._setup_gcp()

        tmp_file = BaseExecutor.save_image_locally(value, image, uuid, 'tmp', 'png')

        filename = "{}_{}.png".format(value, uuid)

        blob = self.bucket.blob('{}/{}'.format(self.bucket_folder_name, filename))

        blob.upload_from_filename(tmp_file, content_type="image/png")

        remove(tmp_file)

        log.info("#image sent to #gcp #bucket",
                 extra=dict(gcp=dict(bucket=self.index, fileName=filename, publicUrl=blob.public_url)))

        return blob.public_url

    def notify(self, title, message, url):
        """
        Send request to pushover_notify API with data:

        token (required) - your application"s API token
        user (required) - the user/group key (not e-mail address) of your user (or you), viewable when logged into our
        dashboard (often referred to as USER_KEY in our documentation and code examples)
        message (required) - your message
        Some optional parameters may be included:
        attachment - an image attachment to send with the message; see attachments for more information on how to
        upload files
        device - your user"s device name to send the message directly to that device, rather than all of the user"s
        devices (multiple devices may be separated by a comma)
        title - your message"s title, otherwise your app"s name is used
        url - a supplementary URL to show with your message
        url_title - a title for your supplementary URL, otherwise just the URL is shown
        priority - send as -2 to generate no notification/alert, -1 to always send as a quiet notification, 1 to
        display as high-priority and bypass the user"s quiet hours, or 2 to also require confirmation from the user
        sound - the name of one of the sounds supported by device clients to override the user"s default sound choice
        timestamp - a Unix timestamp of your message"s date and time to display to the user, rather than the time your
        message is received by our API

        :param title: title for message
        :param message: message
        :param url: optional url to pass
        :return: -
        """
        if self.pushover_config is None:
            self._setup_pushover()

        result = None
        device = "video-analysis"

        request_data = dict(token=self.pushover_config.get("APP_TOKEN", ""),
                            user=self.pushover_config.get("USER_KEY", ""),
                            message=message,
                            device=device,
                            title=title,
                            url=url)

        try:
            log.info("#sending #pushover #notification", extra=dict(pushover=dict(message=message,
                                                                                  title=title,
                                                                                  url=url,
                                                                                  device=device)))

            result = post("https://api.pushover.net/1/messages.json", data=request_data)

            log.info("#delivered #pushover #notification", extra=dict(pushover=dict(message=message,
                                                                                    title=title,
                                                                                    url=url,
                                                                                    device=device)))
        except HTTPError:
            log.error("error while #sending #pushover #notification", exc_info=True)

        return result

    def _action(self, value, confidence, image, uuid, **kwargs):
        file = getattr(self, self.save_file_function)(value, image, uuid)

        self.rdb.set_val(uuid, dict(value=value, confidence=confidence), **dict(kwargs))

        return file

    def _setup_rdb(self):
        self.rdb.init()

    def _setup_gcp(self):
        environ['GOOGLE_APPLICATION_CREDENTIALS'] = "{}/config/gcp/key.json".format(BASE_PATH)

        client = BaseExecutor._get_storage_client()

        self.bucket = client.bucket('video-analysis-file')

        try:
            self.bucket.make_public(recursive=True, future=True)
        except Exception:
            pass

    def _setup_pushover(self):
        self.pushover_config = dict(APP_TOKEN=getenv("PUSHOVER_APP_TOKEN"), USER_KEY=getenv("PUSHOVER_USER_KEY"))

    @staticmethod
    def save_image_locally(value, image, uuid, folder, ext):
        filename = "{}_{}.{}".format(value, uuid, ext)

        full_path = "{}/{}/{}".format(BASE_PATH, folder, filename)

        cv2.imwrite(full_path, image)

        log.info("#saved #image", extra=dict(filePath=full_path, folder=folder, ext=ext))

        return full_path

    @staticmethod
    def skip(*args, **kwargs):
        pass

    @staticmethod
    def _get_storage_client():
        return storage.Client(project=getenv('GCP_PROJECT_ID'))


class FastTrackBaseExecutor(BaseExecutor):
    """

    FastTrackBaseExecutor class should be used when we want to skip checks in Result Database.

    """

    def action(self, value, confidence, image, uuid, **kwargs):
        log.info("fast tracking processing", extra=dict(value=value))

        self._action(value, confidence, image, uuid, **dict(kwargs))

        log.info("#notification send about value", extra=dict(value=value, confidence=confidence))
