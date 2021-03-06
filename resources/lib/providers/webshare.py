"""
    Webshare link resolver.
"""

import xml.etree.ElementTree as ElementTree

import requests
from simpleplugin import Plugin

from resources.lib.const import DOWNLOAD_TYPE, SETTINGS, CACHE
from resources.lib.kodilogging import logger
from resources.lib.settings import settings
from resources.lib.utils.kodiutils import get_screen_width, get_screen_height, common_headers

plugin = Plugin()


class Webshare:
    def __init__(self, username, password, token=None):
        self._username = username
        self._password = password
        self._token = token

    def __repr__(self):
        return self.__class__.__name__

    @property
    def username(self):
        return self._username()

    @property
    def password(self):
        return self._password()

    @property
    def token(self):
        return self._token()

    @plugin.mem_cached(CACHE.EXPIRATION_TIME)
    def get_link_for_file_with_id(self, file_id, download_type=DOWNLOAD_TYPE.VIDEO_STREAM):
        """
        POST /api/file_link/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        data = {
            'ident': file_id,
            'download_type': download_type,
            'device_uuid': settings[SETTINGS.UUID],
            'device_res_x': get_screen_width(),
            'device_res_y': get_screen_height(),
        }
        response = self._post('/file_link/', data=data)
        root = self._parse(response)
        link = self._find(root, 'link')
        logger.debug('Getting file link from provider')
        return link

    def _post(self, path, data=None):
        """
        :type data: dict
        """
        if data is None:
            data = {}
        data.setdefault('wst', self.token)
        logger.debug("WS token %s " % self.token)
        headers = common_headers()
        response = requests.post('https://webshare.cz/api{}'.format(path), data=data, headers=headers)
        logger.debug('Response from provider: %s' % response.content)
        return response.content

    def get_salt(self, username):
        """
        POST /api/salt/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        response = self._post('/salt/', data={'username_or_email': username})
        root = self._parse(response)
        logger.debug('Getting user salt from provider')
        status = self._find(root, 'status')
        if status == 'OK':
            return self._find(root, 'salt')
        else:
            return None

    def get_token(self):
        """
        POST /api/login/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """

        response = self._post('/login/', data={
            'username_or_email': self.username,
            'password': self.password,
            'keep_logged_in': 1,
        })
        root = self._parse(response)
        logger.debug('Getting user token from provider')
        return self._find(root, 'token')

    def get_user_data(self):
        """
        POST /api/user_data/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        response = self._post('/user_data/')
        logger.debug('Getting user data from provider')
        logger.debug(response)
        return self._parse(response)

    def is_vip(self, user_data):
        return self._find(user_data, 'vip') == '1'

    def vip_remains(self, user_data):
        """
        Get user's ramaining days as VIP.
        """
        vip_days = self._find(user_data, 'vip_days')
        logger.debug('VIP days remaining: %s', vip_days)
        return int(vip_days)

    def vip_until(self, user_data):
        return self._find(user_data, 'vip_until')

    def is_valid_token(self, user_data):
        return self._find(user_data, 'status') == 'OK'

    @staticmethod
    def _parse(response):
        return ElementTree.fromstring(response)

    @staticmethod
    def _find(xml, key):
        """Find text for element. If element is not found empty string is returned"""
        return xml.findtext(key, '')
