"""
    Webshare link resolver.
"""

from __future__ import print_function

import hashlib
import xml.etree.ElementTree as ET

import requests
from simpleplugin import Plugin

from resources.lib.const import DOWNLOAD_TYPE, SETTINGS, CACHE
from resources.lib.kodilogging import logger
from resources.lib.settings import settings
from resources.lib.utils.kodiutils import get_screen_width, get_screen_height, common_headers
from resources.lib.vendor.md5crypt import md5crypt

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
        headers = common_headers()
        response = requests.post('https://webshare.cz/api{}'.format(path), data=data, headers=headers)
        logger.debug('Response from provider: %s' % response.content)
        return response.content

    def _get_salt(self):
        """
        POST /api/salt/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        response = self._post('/salt/', data={'username_or_email': self.username})
        root = self._parse(response)
        logger.debug('Getting user salt from provider')
        try:
            return self._find(root, 'salt')
        except AttributeError:
            pass

    def get_token(self):
        """
        POST /api/login/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        salt = self._get_salt()
        if salt:
            hashed = self._hash_password(self.password, salt)

            response = self._post('/login/', data={
                'username_or_email': self.username,
                'password': hashed,
                'keep_logged_in': 1,
            })
            root = self._parse(response)
            logger.debug('Getting user token from provider')
            try:
                return self._find(root, 'token')
            except AttributeError:
                pass

    def get_user_data(self):
        """
        POST /api/salt/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        response = self._post('/user_data/')
        logger.debug('Getting user data from provider')
        return self._parse(response)

    def is_vip(self, user_data):
        vip = self._find(user_data, 'vip')
        return vip == '1'

    def vip_remains(self, user_data):
        vip_days = self._find(user_data, 'vip_days')
        logger.debug('VIP days remaining: %s', vip_days)
        return int(vip_days)

    def is_valid_token(self, user_data):
        return self._find(user_data, 'status') == 'OK'

    @staticmethod
    def _parse(response):
        return ET.fromstring(response)

    @staticmethod
    def _find(xml, key):
        return xml.find(key).text



    @classmethod
    def _hash_password(cls, password, salt):
        """Creates password hash used by Webshare API"""
        return hashlib.sha1(md5crypt(password, salt=salt).encode('utf-8')).hexdigest()
